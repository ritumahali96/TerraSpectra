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
