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

np.save("week1_data_processing/salinas_cube_pca.npy", cube_pca)

np.save("week1_data_processing/salinas_gt.npy", gt)

import matplotlib.pyplot as plt

false_color = cube_norm[:, :, [29, 19, 9]]
plt.imshow(false_color)
plt.title("False-Color Composite")
plt.savefig("week1_data_processing/false_color.png")
plt.close()

plt.imshow(gt, cmap="tab20")
plt.title("Ground Truth")
plt.savefig("week1_data_processing/ground_truth.png")
plt.close()

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
for i in range(3):
    axes[i].imshow(cube_pca[:, :, i], cmap="viridis")
    axes[i].set_title(f"PCA Component {i+1}")
plt.savefig("week1_data_processing/pca_components.png")
plt.close()

plt.plot(np.cumsum(pca.explained_variance_ratio_) * 100, marker="o")
plt.axhline(95, color="red", linestyle="--")
plt.xlabel("Number of Components")
plt.ylabel("Cumulative Variance (%)")
plt.title("PCA Explained Variance")
plt.savefig("week1_data_processing/variance_plot.png")
plt.close()
