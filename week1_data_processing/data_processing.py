import scipy.io as sio
import numpy as np

# Load hyperspectral cube and ground truth
loaded_data = sio.loadmat("salinas_corrected.mat")
cube = loaded_data["salinas_corrected"]

gt_data = sio.loadmat("salinas_gt.mat")
gt = gt_data["salinas_gt"]

print("Cube shape:", cube.shape)
print("GT shape:", gt.shape)

cube = cube.astype(np.float32)
H, W, B = cube.shape
cube_norm = np.zeros_like(cube)

for b in range(B):
    band = cube[:, :, b]
    band_min = band.min()
    band_max = band.max()
    cube_norm[:, :, b] = (band - band_min) / (band_max - band_min + 1e-8)
