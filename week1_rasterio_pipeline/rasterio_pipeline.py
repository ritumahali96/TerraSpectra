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
