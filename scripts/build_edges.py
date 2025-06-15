import argparse
import csv
import os
import math
import io

from PIL import Image
import rasterio
import redis
import osmnx as ox
from geopy.distance import geodesic


def read_elevation(lat, lon, srtm_dir):
    """Return elevation for given lat/lon from SRTM tiles."""
    lat_deg = int(math.floor(lat))
    lon_deg = int(math.floor(lon))
    tile_name = f"N{lat_deg:02d}E{lon_deg:03d}.SRTMGL1.hgt.zip"
    path = os.path.join(srtm_dir, tile_name)
    if not os.path.exists(path):
        return None
    with rasterio.open(path) as src:
        row, col = src.index(lon, lat)
        return src.read(1)[row, col].item()


def tilexy(lon, lat, zoom):
    n = 2**zoom
    xtile = (lon + 180.0) / 360.0 * n
    lat_rad = math.radians(lat)
    ytile = (
        (1 - (math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi)) / 2 * n
    )
    return int(xtile), int(ytile), xtile - int(xtile), ytile - int(ytile)


def read_aqi(redis_url, aqi_dir, lon, lat, zoom=11):
    x, y, dx, dy = tilexy(lon, lat, zoom)
    key = f"aqi:{zoom}:{x}:{y}"
    client = None
    if redis_url:
        client = redis.Redis.from_url(redis_url)
        data = client.get(key)
        if data:
            img = Image.open(io.BytesIO(data))
        else:
            img = None
    else:
        img = None
    if img is None:
        local_path = os.path.join(aqi_dir, str(zoom), f"{x}_{y}.png")
        if os.path.exists(local_path):
            img = Image.open(local_path)
    if img is None:
        return None
    px = img.getpixel((int(dx * img.width), int(dy * img.height)))
    return sum(px[:3]) / 3


def main():
    parser = argparse.ArgumentParser(description="Build edges.tsv from OSM data")
    parser.add_argument("city", help="City PBF base name (without .osm.pbf)")
    parser.add_argument(
        "--data-dir", default="data", help="Directory with PBF and tiles"
    )
    parser.add_argument(
        "--srtm-dir", default="data/srtm", help="Directory with SRTM tiles"
    )
    parser.add_argument(
        "--aqi-dir", default="data/aqi", help="Directory with AQI tiles"
    )
    parser.add_argument("--redis-url", default=os.environ.get("REDIS_URL"))
    parser.add_argument("--out", default="edges.tsv")
    args = parser.parse_args()

    # pbf_path = os.path.join(args.data_dir, f"{args.city}.osm.pbf")
    # G = ox.graph_from_file(pbf_path, retain_all=False)
    osm_path = os.path.join(args.data_dir, f"{args.city}.osm")
    G = ox.graph_from_xml(osm_path, retain_all=False)

    print("Loaded graph!")
    print(f"Number of nodes: {G.number_of_nodes()}, edges: {G.number_of_edges()}")

    with open(args.out, "w", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(
            [
                "from_lon",
                "from_lat",
                "to_lon",
                "to_lat",
                "distance_m",
                "aqi",
                "elevation_gain_m",
            ]
        )

        for u, v, data in G.edges(data=True):
            if "geometry" in data:
                lon1, lat1 = data["geometry"].coords[0]
                lon2, lat2 = data["geometry"].coords[-1]
            else:
                lon1 = G.nodes[u]["x"]
                lat1 = G.nodes[u]["y"]
                lon2 = G.nodes[v]["x"]
                lat2 = G.nodes[v]["y"]
            dist = geodesic((lat1, lon1), (lat2, lon2)).meters
            elev1 = read_elevation(lat1, lon1, args.srtm_dir)
            elev2 = read_elevation(lat2, lon2, args.srtm_dir)
            if elev1 is not None and elev2 is not None:
                gain = max(0, elev2 - elev1)
            else:
                gain = ""
            aqi_vals = []
            for frac in [i / 10 for i in range(11)]:
                lat = lat1 + frac * (lat2 - lat1)
                lon = lon1 + frac * (lon2 - lon1)
                aqi = read_aqi(args.redis_url, args.aqi_dir, lon, lat)
                if aqi is not None:
                    aqi_vals.append(aqi)
            avg_aqi = sum(aqi_vals) / len(aqi_vals) if aqi_vals else ""
            writer.writerow([lon1, lat1, lon2, lat2, round(dist, 1), avg_aqi, gain])


if __name__ == "__main__":
    main()
