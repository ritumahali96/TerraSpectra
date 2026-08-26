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

print("Normalization done. Value range:", cube_norm.min(), "-", cube_norm.max())

from sklearn.decomposition import PCA

flat = cube_norm.reshape(-1, B)
pca = PCA(n_components=15)
flat_pca = pca.fit_transform(flat)
cube_pca = flat_pca.reshape(H, W, 15)

total_variance = pca.explained_variance_ratio_.sum() * 100
print(f"Variance preserved: {total_variance:.2f}%")
