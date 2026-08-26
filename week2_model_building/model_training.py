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

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    patches, labels, test_size=0.2, random_state=42, stratify=labels
)

print("Training samples:", X_train.shape[0])
print("Testing samples:", X_test.shape[0])

# Rearrange dimensions: bands become the depth dimension for Conv3D
X_train = np.transpose(X_train, (0, 3, 1, 2))
X_test = np.transpose(X_test, (0, 3, 1, 2))

X_train = torch.tensor(X_train, dtype=torch.float32).unsqueeze(1)
X_test = torch.tensor(X_test, dtype=torch.float32).unsqueeze(1)
y_train = torch.tensor(y_train, dtype=torch.long)
y_test = torch.tensor(y_test, dtype=torch.long)

print("Final training tensor shape:", X_train.shape)
print("Final testing tensor shape:", X_test.shape)

class Simple3DCNN(nn.Module):
    def __init__(self, num_classes=16):
        super(Simple3DCNN, self).__init__()
        self.conv1 = nn.Conv3d(in_channels=1, out_channels=8, kernel_size=(3, 3, 3), padding=1)
        self.conv2 = nn.Conv3d(in_channels=8, out_channels=16, kernel_size=(3, 3, 3), padding=1)

        self.dropout = nn.Dropout(0.4)
        self.fc1 = nn.Linear(16 * 15 * 5 * 5, 128)
        self.fc2 = nn.Linear(128, num_classes)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = x.view(x.size(0), -1)
        x = self.dropout(x)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x

model = Simple3DCNN(num_classes=16).to(device)
print(model)

from torch.utils.data import TensorDataset, DataLoader

train_dataset = TensorDataset(X_train, y_train)
test_dataset = TensorDataset(X_test, y_test)

train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)
