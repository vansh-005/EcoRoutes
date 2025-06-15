import os

# Settings
tile_folder = './data/aqi'
tile_size = 256
z = 8  # Your zoom level

# Calculate degrees per tile at this zoom
def tile2lon(x, z):
    return x / (2 ** z) * 360.0 - 180.0

def tile2lat(y, z):
    n = 3.141592653589793 - 2.0 * 3.141592653589793 * y / (2 ** z)
    return 180.0 / 3.141592653589793 * \
        (2.0 * atan(exp(n)) - 3.141592653589793 / 2.0)

from math import atan, exp

for fname in os.listdir(tile_folder):
    if fname.endswith('.png'):
        parts = fname[:-4].split('_')
        if len(parts) != 2:
            continue
        x, y = map(int, parts)
        # World file parameters
        # Pixel size in X direction (longitude delta per pixel)
        res = 360.0 / (2 ** z) / tile_size
        x_min = tile2lon(x, z)
        y_max = 85.05112878 - (y / (2 ** z)) * 170.10225756  # Web Mercator's limits

        pgw_content = f"""{res}
0.0
0.0
{-res}
{x_min}
{y_max}
"""
        with open(os.path.join(tile_folder, f"{x}_{y}.pgw"), 'w') as f:
            f.write(pgw_content)
