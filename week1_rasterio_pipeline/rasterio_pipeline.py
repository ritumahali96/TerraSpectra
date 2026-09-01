import rasterio
from rasterio.transform import from_origin
import scipy.io as sio
import numpy as np

# Load original Salinas hyperspectral data
loaded_data = sio.loadmat("salinas_corrected.mat")
cube = loaded_data["salinas_corrected"]

gt_data = sio.loadmat("salinas_gt.mat")
gt = gt_data["salinas_gt"]

print("Cube shape:", cube.shape)

# Prepare cube for GeoTIFF export
H, W, B = cube.shape
cube_for_tiff = np.transpose(cube, (2, 0, 1)).astype(np.float32)

# Define fake geographic transform for Salinas Valley coordinates
transform = from_origin(-121.65, 36.68, 0.0000333, 0.0000333)

# Write the hyperspectral cube as a GeoTIFF file using Rasterio
with rasterio.open(
    "salinas_hyperspectral.tif", "w", driver="GTiff",
    height=H, width=W, count=B, dtype=cube_for_tiff.dtype,
    crs="EPSG:4326", transform=transform,
) as dst:
    dst.write(cube_for_tiff)

print("GeoTIFF file created")
