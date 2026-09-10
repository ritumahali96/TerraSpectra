import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import TensorDataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report
import numpy as np
import scipy.io as sio # To load gt data
import matplotlib.pyplot as plt
import seaborn as sns
import os

# --- Configuration and Device Setup ---
# Use GPU if available, otherwise CPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", device)

# --- Data Loading (from Week 1 outputs) ---
# Assuming week1_rasterio_pipeline has been executed and saved these files
# Adjust paths if the script is run from a different directory
try:
    cube_pca_rasterio = np.load("week1_rasterio_pipeline/cube_pca_rasterio.npy")
    gt_data = sio.loadmat("/TerraSpectra Dataset/salinas_gt.mat") # original gt file path
    gt = gt_data["salinas_gt"]
    print(f"Loaded PCA cube shape: {cube_pca_rasterio.shape}")
    print(f"Loaded Ground Truth shape: {gt.shape}")
except FileNotFoundError:
    print("Error: Week 1 pipeline outputs (cube_pca_rasterio.npy or salinas_gt.mat) not found.")
    print("Please ensure the Week 1 pipeline has been run and outputs are accessible.")
    exit() # Exit if data is not found for a standalone script

# --- Patch extraction function (from Week 2) ---
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
            labels.append(label - 1) # Shift labels to start from 0 for PyTorch
    return np.array(patches), np.array(labels)

# --- Data Preparation for SpectralViT ---
patches_vit, labels_vit = create_patches(cube_pca_rasterio, gt, patch_size=5)
print("Patches shape for ViT:", patches_vit.shape)
print("Labels shape for ViT:", labels_vit.shape)

X_train_vit, X_test_vit, y_train_vit, y_test_vit = train_test_split(
    patches_vit, labels_vit, test_size=0.2, random_state=42, stratify=labels_vit
)

# PyTorch expects shape: (batch, channels, depth, height, width)
# Our patches are (samples, H, W, bands), convert to (samples, 1, bands, H, W)
X_train_vit = np.transpose(X_train_vit, (0, 3, 1, 2))
X_test_vit = np.transpose(X_test_vit, (0, 3, 1, 2))

# Add a channel dimension (which will be squeezed later by ViT)
X_train_vit = torch.tensor(X_train_vit, dtype=torch.float32).unsqueeze(1)
X_test_vit = torch.tensor(X_test_vit, dtype=torch.float32).unsqueeze(1)
y_train_vit = torch.tensor(y_train_vit, dtype=torch.long)
y_test_vit = torch.tensor(y_test_vit, dtype=torch.long)

print("Final training tensor shape for ViT:", X_train_vit.shape)
print("Final testing tensor shape for ViT:", X_test_vit.shape)

# --- SpectralViT Model Architecture ---
class MultiHeadSelfAttention(nn.Module):
    def __init__(self, embed_dim, num_heads):
        super().__init__()
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads
        assert self.head_dim * num_heads == self.embed_dim, "embed_dim must be divisible by num_heads"

        self.qkv_proj = nn.Linear(embed_dim, 3 * embed_dim)
        self.o_proj = nn.Linear(embed_dim, embed_dim)

    def forward(self, x):
        batch_size, seq_len, _ = x.shape
        qkv = self.qkv_proj(x).reshape(batch_size, seq_len, 3, self.num_heads, self.head_dim)
        qkv = qkv.permute(2, 0, 3, 1, 4) # (3, batch_size, num_heads, seq_len, head_dim)
        q, k, v = qkv[0], qkv[1], qkv[2]

        attention_scores = torch.matmul(q, k.transpose(-2, -1)) / (self.head_dim ** 0.5)
        attention_probs = F.softmax(attention_scores, dim=-1)

        output = torch.matmul(attention_probs, v)
        output = output.permute(0, 2, 1, 3).reshape(batch_size, seq_len, self.embed_dim)
        output = self.o_proj(output)
        return output

class TransformerBlock(nn.Module):
    def __init__(self, embed_dim, num_heads, mlp_dim, dropout=0.1):
        super().__init__()
        self.norm1 = nn.LayerNorm(embed_dim)
        self.attn = MultiHeadSelfAttention(embed_dim, num_heads)
        self.norm2 = nn.LayerNorm(embed_dim)
        self.mlp = nn.Sequential(
            nn.Linear(embed_dim, mlp_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(mlp_dim, embed_dim),
            nn.Dropout(dropout),
        )

    def forward(self, x):
        x = x + self.attn(self.norm1(x))
        x = x + self.mlp(self.norm2(x))
        return x

class SpectralViT(nn.Module):
    def __init__(self, input_bands, spatial_features, embed_dim, num_heads, num_layers, mlp_dim, num_classes, dropout=0.1):
        super().__init__()
        self.input_bands = input_bands
        self.spatial_features = spatial_features
        self.embed_dim = embed_dim

        self.projection = nn.Linear(self.spatial_features, embed_dim)
        self.positional_embedding = nn.Parameter(torch.randn(1, self.input_bands, embed_dim))
        self.transformer_encoder = nn.Sequential(
            *[TransformerBlock(embed_dim, num_heads, mlp_dim, dropout) for _ in range(num_layers)]
        )
        self.mlp_head = nn.Sequential(
            nn.LayerNorm(embed_dim),
            nn.Linear(embed_dim, mlp_dim),
            nn.GELU(),
            nn.Linear(mlp_dim, num_classes)
        )

    def forward(self, x):
        x = x.squeeze(1).reshape(x.size(0), self.input_bands, self.spatial_features)
        x = self.projection(x)
        x = x + self.positional_embedding
        x = self.transformer_encoder(x)
        x = x.mean(dim=1) # Aggregate across band dimension
        logits = self.mlp_head(x)
        return logits

# Instantiate the SpectralViT model
vit_model = SpectralViT(
    input_bands=cube_pca_rasterio.shape[2],
    spatial_features=5*5,
    embed_dim=128,
    num_heads=4,
    num_layers=4,
    mlp_dim=256,
    num_classes=16,
    dropout=0.1
).to(device)
print(vit_model)

# --- Training Setup and Loop for SpectralViT ---
train_dataset_vit = TensorDataset(X_train_vit, y_train_vit)
test_dataset_vit = TensorDataset(X_test_vit, y_test_vit)

train_loader_vit = DataLoader(train_dataset_vit, batch_size=64, shuffle=True)
test_loader_vit = DataLoader(test_dataset_vit, batch_size=64, shuffle=False)

criterion_vit = nn.CrossEntropyLoss()
optimizer_vit = torch.optim.Adam(vit_model.parameters(), lr=0.001)

print("ViT Training setup ready. Number of batches per epoch:", len(train_loader_vit))

num_epochs_vit = 50
accuracy_values_vit = []
loss_values_vit = []

for epoch in range(num_epochs_vit):
    vit_model.train()
    running_loss_vit = 0.0
    correct_vit = 0
    total_vit = 0

    for batch_X_vit, batch_y_vit in train_loader_vit:
        batch_X_vit, batch_y_vit = batch_X_vit.to(device), batch_y_vit.to(device)

        optimizer_vit.zero_grad()
        outputs_vit = vit_model(batch_X_vit)
        loss_vit = criterion_vit(outputs_vit, batch_y_vit)
        loss_vit.backward()
        optimizer_vit.step()

        running_loss_vit += loss_vit.item()
        _, predicted_vit = torch.max(outputs_vit, 1)
        correct_vit += (predicted_vit == batch_y_vit).sum().item()
        total_vit += batch_y_vit.size(0)

    epoch_loss_vit = running_loss_vit / len(train_loader_vit)
    epoch_acc_vit = 100 * correct_vit / total_vit
    accuracy_values_vit.append(epoch_acc_vit)
    loss_values_vit.append(epoch_loss_vit)
    print(f"Epoch [{epoch+1}/{num_epochs_vit}] - ViT Loss: {epoch_loss_vit:.4f} - ViT Accuracy: {epoch_acc_vit:.2f}%")

# --- Test Set Evaluation for SpectralViT ---
vit_model.eval()
correct_vit = 0
total_vit = 0

all_predictions = []
all_true_labels = []

with torch.no_grad():
    for batch_X_vit, batch_y_vit in test_loader_vit:
        batch_X_vit, batch_y_vit = batch_X_vit.to(device), batch_y_vit.to(device)
        outputs_vit = vit_model(batch_X_vit)
        _, predicted_vit = torch.max(outputs_vit, 1)
        correct_vit += (predicted_vit == batch_y_vit).sum().item()
        total_vit += batch_y_vit.size(0)

        all_predictions.extend(predicted_vit.cpu().numpy())
        all_true_labels.extend(batch_y_vit.cpu().numpy())


test_accuracy_vit = 100 * correct_vit / total_vit
print(f"ViT Test Accuracy: {test_accuracy_vit:.2f}%")

# Convert lists to numpy arrays for metrics calculation
all_predictions = np.array(all_predictions)
all_true_labels = np.array(all_true_labels)

# Generate and save Confusion Matrix
cm = confusion_matrix(all_true_labels, all_predictions)
plt.figure(figsize=(12, 10))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.title('Confusion Matrix for SpectralViT (Test Set)')
plt.xlabel('Predicted Label')
plt.ylabel('True Label')
os.makedirs('week3_spectral_vit_modeling/results', exist_ok=True)
plt.savefig('week3_spectral_vit_modeling/results/confusion_matrix.png')
plt.close() # Close the plot to free memory

# Generate and save Classification Report
report = classification_report(all_true_labels, all_predictions, digits=4, output_dict=True)
print("\nClassification Report for SpectralViT (Test Set):\n")
print(classification_report(all_true_labels, all_predictions, digits=4))

# Save classification report to a file
with open('week3_spectral_vit_modeling/results/classification_report.txt', 'w') as f:
    f.write(classification_report(all_true_labels, all_predictions, digits=4))

# End of Week 3: Vision Transformer (ViT) Model for Spectral Attention pipeline
# Pipeline: GeoTIFF -> Rasterio parse -> PCA -> Patch Extraction -> SpectralViT Training -> Evaluation
