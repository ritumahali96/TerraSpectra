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

# Parse the GeoTIFF file back using Rasterio
with rasterio.open("salinas_hyperspectral.tif") as src:
    print("Number of bands:", src.count)
    print("Coordinate system:", src.crs)
    parsed_cube = src.read()

# Rearrange to (height, width, bands) format
parsed_cube = np.transpose(parsed_cube, (1, 2, 0))
print("Parsed cube shape:", parsed_cube.shape)

# Normalize each spectral band to 0-1 range
H, W, B = parsed_cube.shape
cube_norm = np.zeros_like(parsed_cube)

for b in range(B):
    band = parsed_cube[:, :, b]
    band_min, band_max = band.min(), band.max()
    cube_norm[:, :, b] = (band - band_min) / (band_max - band_min + 1e-8)

print("Normalization done")

from sklearn.decomposition import PCA

flat = cube_norm.reshape(-1, B)

pca = PCA(n_components=15)
flat_pca = pca.fit_transform(flat)
cube_pca_rasterio = flat_pca.reshape(H, W, 15)

total_variance = pca.explained_variance_ratio_.sum() * 100
print(f"Variance preserved: {total_variance:.2f}%")

np.save("week1_rasterio_pipeline/cube_pca_rasterio.npy", cube_pca_rasterio)

# End of Rasterio-based Week 1 pipeline
# Pipeline: .mat -> GeoTIFF -> Rasterio parse -> normalize -> PCA

# --- Week 2: 3D-CNN Model Training (using Rasterio-derived data) ---
import torch
import torch.nn as nn
import torch.nn.functional as F

# --- Week 2: 3D-CNN Model Training (using Rasterio-derived data) ---
import torch
import torch.nn as nn
import torch.nn.functional as F

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", device)

def create_patches(cube, gt, patch_size=5):
    margin = patch_size // 2
    padded_cube = np.pad(cube, ((margin, margin), (margin, margin), (0, 0)), mode="reflect")
    patches = []
    labels = []
    H, W, B = cube.shape
    for i in range(H):
        for j in range(W):
            label = gt[i, j]
            if label == 0:
                continue
            patch = padded_cube[i:i+patch_size, j:j+patch_size, :]
            patches.append(patch)
            labels.append(label - 1)
    return np.array(patches), np.array(labels)

patches, labels = create_patches(cube_pca_rasterio, gt, patch_size=5)
print("Patches shape:", patches.shape)
print("Labels shape:", labels.shape)

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    patches, labels, test_size=0.2, random_state=42, stratify=labels
)
print("Training samples:", X_train.shape[0])
print("Testing samples:", X_test.shape[0])

# PyTorch expects shape: (batch, channels, depth, height, width)
# our patches are currently (samples, height, width, bands) - need to rearrange
X_train = np.transpose(X_train, (0, 3, 1, 2))    # move bands to act as the "depth" dimension
X_test = np.transpose(X_test, (0, 3, 1, 2))

# convert numpy arrays into PyTorch tensors (the format PyTorch models understand)
X_train = torch.tensor(X_train, dtype=torch.float32).unsqueeze(1)   # add a "channel" dimension (required by Conv3D)
X_test = torch.tensor(X_test, dtype=torch.float32).unsqueeze(1)
y_train = torch.tensor(y_train, dtype=torch.long)                    # convert labels to PyTorch's integer tensor format
y_test = torch.tensor(y_test, dtype=torch.long)

print("Final training tensor shape:", X_train.shape)
print("Final testing tensor shape:", X_test.shape)
