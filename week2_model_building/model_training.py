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

criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

print("Training setup ready. Number of batches per epoch:", len(train_loader))

num_epochs = 15
accuracy_values = []
loss_values = []

for epoch in range(num_epochs):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    for batch_X, batch_y in train_loader:
        batch_X, batch_y = batch_X.to(device), batch_y.to(device)

        optimizer.zero_grad()
        outputs = model(batch_X)
        loss = criterion(outputs, batch_y)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()
        _, predicted = torch.max(outputs, 1)
        correct += (predicted == batch_y).sum().item()
        total += batch_y.size(0)

    epoch_loss = running_loss / len(train_loader)
    epoch_acc = 100 * correct / total
    accuracy_values.append(epoch_acc)
    loss_values.append(epoch_loss)
    print(f"Epoch [{epoch+1}/{num_epochs}] - Loss: {epoch_loss:.4f} - Accuracy: {epoch_acc:.2f}%")
    

import matplotlib.pyplot as plt

epochs = list(range(1, num_epochs + 1))
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].plot(epochs, accuracy_values, marker="o", color="green")
axes[0].set_title("Training Accuracy over Epochs")
axes[0].set_xlabel("Epoch")
axes[0].set_ylabel("Accuracy (%)")
axes[0].grid(alpha=0.3)

axes[1].plot(epochs, loss_values, marker="o", color="red")
axes[1].set_title("Training Loss over Epochs")
axes[1].set_xlabel("Epoch")
axes[1].set_ylabel("Loss")
axes[1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig("week2_model_building/training_curves.png", dpi=150)
plt.close()

model.eval()
correct = 0
total = 0

with torch.no_grad():
    for batch_X, batch_y in test_loader:
        batch_X, batch_y = batch_X.to(device), batch_y.to(device)
        outputs = model(batch_X)
        _, predicted = torch.max(outputs, 1)
        correct += (predicted == batch_y).sum().item()
        total += batch_y.size(0)

test_accuracy = 100 * correct / total
print(f"Test Accuracy: {test_accuracy:.2f}%")
