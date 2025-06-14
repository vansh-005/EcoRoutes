import sys
import os
import math
import requests
from tqdm import tqdm

MINLON, MINLAT, MAXLON, MAXLAT, OUTDIR = float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
os.makedirs(OUTDIR, exist_ok=True)

def download_tile(lat, lon, outdir):
    fname = f"N{abs(int(lat)):02d}E{abs(int(lon)):03d}.SRTMGL1.hgt.zip"
    url = f"https://s3.amazonaws.com/elevation-tiles-prod/skadi/{'N'+str(abs(int(lat))).zfill(2)}/N{abs(int(lat)):02d}E{abs(int(lon)):03d}.hgt.gz"
    dest = os.path.join(outdir, fname)
    if not os.path.exists(dest):
        resp = requests.get(url, stream=True)
        if resp.ok:
            with open(dest, 'wb') as f:
                for chunk in resp.iter_content(1024*1024):
                    f.write(chunk)
            print(f"Downloaded {fname}")
        else:
            print(f"Failed for {fname}")

for lat in range(math.floor(MINLAT), math.ceil(MAXLAT)):
    for lon in range(math.floor(MINLON), math.ceil(MAXLON)):
        download_tile(lat, lon, OUTDIR)
