import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", device)

# Load PCA-reduced cube and ground truth from Week 1
cube_pca = np.load("salinas_cube_pca.npy")
gt = np.load("salinas_gt.npy")

print("Cube shape:", cube_pca.shape)
print("GT shape:", gt.shape)

def create_patches(cube, gt, patch_size=5):
    # Extracts a small spatial-spectral window around each labeled pixel
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

patches, labels = create_patches(cube_pca, gt, patch_size=5)

print("Patches shape:", patches.shape)
print("Labels shape:", labels.shape)
print("Number of classes:", len(np.unique(labels)))
