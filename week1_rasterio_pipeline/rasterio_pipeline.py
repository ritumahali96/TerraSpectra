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

class Simple3DCNN(nn.Module):                          # define our neural network as a class
    def __init__(self, num_classes=16):                # constructor, runs once when model is created
        super(Simple3DCNN, self).__init__()             # required setup for all PyTorch models

        # first 3D convolution layer: 1 input channel -> 8 filters, each scanning a 3x3x3 window
        self.conv1 = nn.Conv3d(in_channels=1, out_channels=8, kernel_size=(3, 3, 3), padding=1)

        # second 3D convolution layer: 8 -> 16 filters, learning more complex patterns
        self.conv2 = nn.Conv3d(in_channels=8, out_channels=16, kernel_size=(3, 3, 3), padding=1)

        # dropout randomly disables 40% of neurons during training to prevent overfitting
        self.dropout = nn.Dropout(0.4)

        # fully connected layer: flatten conv output and compress to 128 features
        self.fc1 = nn.Linear(16 * 15 * 5 * 5, 128)

        # final layer: 128 features -> 16 output scores, one per crop class
        self.fc2 = nn.Linear(128, num_classes)

    def forward(self, x):                                # defines how data flows through the layers
        x = F.relu(self.conv1(x))                        # apply first conv layer, then ReLU activation
        x = F.relu(self.conv2(x))                         # apply second conv layer, then ReLU activation
        x = x.view(x.size(0), -1)                          # flatten into a 1D vector per sample
        x = self.dropout(x)                                 # apply dropout
        x = F.relu(self.fc1(x))                             # first dense layer with ReLU
        x = self.fc2(x)                                      # final output layer (raw class scores)
        return x

# create the model and move it to GPU (if available)
model = Simple3DCNN(num_classes=16).to(device)          # instantiate the model
print(model)                                              # print architecture to verify it's built correctly

from torch.utils.data import TensorDataset, DataLoader   # tools for batching data efficiently

# combine features and labels into a single dataset object
train_dataset = TensorDataset(X_train, y_train)
test_dataset = TensorDataset(X_test, y_test)

# DataLoader splits data into small batches and shuffles training data each epoch
train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)

# loss function - measures how wrong the model's predictions are
criterion = nn.CrossEntropyLoss()

# optimizer - updates model weights to reduce the loss (Adam is a reliable, popular choice)
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

print("Training setup ready. Number of batches per epoch:", len(train_loader))

num_epochs = 15   # how many times the model will see the entire training dataset
accuracy_values = []    # list to store accuracy after each epoch
loss_values = []        # list to store loss after each epoch

for epoch in range(num_epochs):                        # repeat this process 15 times (15 epochs)
    model.train()                                        # set model to training mode (enables dropout)
    running_loss = 0.0                                    # track total loss for this epoch
    correct = 0                                            # track number of correct predictions
    total = 0                                              # track total number of predictions made

    for batch_X, batch_y in train_loader:                 # loop through each batch of 64 samples
        batch_X, batch_y = batch_X.to(device), batch_y.to(device)   # move this batch to GPU

        optimizer.zero_grad()                              # clear gradients from the previous batch
        outputs = model(batch_X)                            # forward pass: get model's predictions
        loss = criterion(outputs, batch_y)                   # calculate how wrong the predictions are

        loss.backward()                                       # backward pass: calculate how to adjust weights
        optimizer.step()                                       # actually update the model's weights

        running_loss += loss.item()                          # add this batch's loss to the running total
        _, predicted = torch.max(outputs, 1)                   # get the predicted class (highest score)
        correct += (predicted == batch_y).sum().item()          # count how many predictions were correct
        total += batch_y.size(0)                                 # count total samples processed

    epoch_loss = running_loss / len(train_loader)            # calculate average loss for this epoch
    epoch_acc = 100 * correct / total                          # calculate accuracy percentage for this epoch
    accuracy_values.append(epoch_acc)                          # save this epoch's accuracy
    loss_values.append(epoch_loss)                              # save this epoch's loss
    print(f"Epoch [{epoch+1}/{num_epochs}] - Loss: {epoch_loss:.4f} - Accuracy: {epoch_acc:.2f}%")

model.eval()                                    # set model to evaluation mode (disables dropout)
correct = 0
total = 0
