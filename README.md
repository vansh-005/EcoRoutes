# EcoRoutes

This project uses Docker Compose to spin up a routing stack consisting of OSRM,
Redis, and a small Node backend. The backend periodically fetches AQI tiles and
exposes an API for retrieving cached tiles or routing information.

## Backend API

The backend image now starts `node index.js`, which runs an Express server.
Routes:

- `GET /aqi/:z/:x/:y.png` – returns a cached AQI tile from Redis.
- `GET /route?start=lon,lat&end=lon,lat` – proxies a route request to the OSRM service.

The separate `aqi-fetcher` service continues running `scripts/fetch-aqi.js` to
update the cache.

## Preparing data

### Download the OSM extract

The `makefile` looks for `data/northern-zone-latest.osm.pbf` by default. Use
`wget` (or any tool you prefer) to fetch the file from [Geofabrik](https://download.geofabrik.de)
or another OSM mirror:

```bash
wget -O data/northern-zone-latest.osm.pbf \
  https://download.geofabrik.de/path/to/northern-zone-latest.osm.pbf
```

Adjust the URL or the `CITY` variable in `makefile` if you need a different
region.

### Fetch SRTM elevation tiles

Elevation data is downloaded with `scripts/download_srtm.py`. Provide the
bounding box and an output directory (defaults used by `build_edges.py` expect
`data/srtm`):

```bash
python scripts/download_srtm.py MINLON MINLAT MAXLON MAXLAT data/srtm
```

### AQI tiles and world files

AQI PNG tiles should be stored in `data/aqi`. After fetching the tiles (for
example via `backend/scripts/fetch-aqi.js`), generate `.pgw` world files so the
tiles can be georeferenced:

```bash
python make_worldfiles.py
```

This script scans `data/aqi/*.png` and writes matching `.pgw` files alongside
each image.
