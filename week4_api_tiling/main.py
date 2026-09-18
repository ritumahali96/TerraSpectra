
import os
import numpy as np
import rasterio
import torch
import torch.nn as nn
import torch.nn.functional as F
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import joblib
from rasterio.windows import Window
from typing import List, Tuple

# --- Configuration and Device Setup ---
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# --- Load Models ---
try:
    # Load PCA model
    pca = joblib.load("week4_api_tiling/pca_model.joblib")
    print("PCA model loaded successfully.")
except FileNotFoundError:
    raise RuntimeError("pca_model.joblib not found. Ensure it's saved in week4_api_tiling/")

# Define the SpectralViT model architecture (must match the trained model)
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
        x = x.mean(dim=1)
        logits = self.mlp_head(x)
        return logits

# Instantiate the ViT model with the same parameters as during training
# Assuming PCA reduced to 15 bands, patch size 5x5
vit_model = SpectralViT(
    input_bands=15,
    spatial_features=5*5,
    embed_dim=128,
    num_heads=4,
    num_layers=4,
    mlp_dim=256,
    num_classes=16,
    dropout=0.1
).to(device)

try:
    vit_model.load_state_dict(torch.load("week4_api_tiling/spectral_vit_model_state_dict.pth", map_location=device))
    vit_model.eval()
    print("SpectralViT model state dictionary loaded successfully.")
except FileNotFoundError:
    raise RuntimeError("spectral_vit_model_state_dict.pth not found. Ensure it's saved in week4_api_tiling/")


# --- Preprocessing Functions ---
def normalize_band(band_data):
    min_val, max_val = band_data.min(), band_data.max()
    if max_val == min_val:
        return np.zeros_like(band_data)
    return (band_data - min_val) / (max_val - min_val)

def preprocess_tile(tile_data, pca_model, patch_size=5):
    # tile_data shape: (bands, height, width)
    # Transpose to (height, width, bands) for PCA and patch extraction
    H, W, B_raw = tile_data.shape[1], tile_data.shape[2], tile_data.shape[0]
    cube_hw_b = np.transpose(tile_data, (1, 2, 0))

    # Normalize each band
    cube_norm = np.zeros_like(cube_hw_b, dtype=np.float32)
    for b in range(B_raw):
        cube_norm[:, :, b] = normalize_band(cube_hw_b[:, :, b])

    # Apply PCA
    flat_normalized = cube_norm.reshape(-1, B_raw)
    flat_pca = pca_model.transform(flat_normalized) # Use transform, not fit_transform
    cube_pca = flat_pca.reshape(H, W, pca_model.n_components_)

    # Extract patches (similar to create_patches, but without ground truth labels)
    margin = patch_size // 2
    padded_cube = np.pad(cube_pca, ((margin, margin), (margin, margin), (0, 0)), mode="reflect")

    patches = []
    # Iterate through each pixel to get a patch centered around it
    for i in range(H):
        for j in range(W):
            patch = padded_cube[i:i+patch_size, j:j+patch_size, :]
            patches.append(patch)
    
    if not patches:
        return np.array([]), (H, W)

    patches_array = np.array(patches, dtype=np.float32)

    # Reshape for PyTorch (batch, channel, bands, H, W)
    patches_tensor = torch.tensor(patches_array, dtype=torch.float32)
    patches_tensor = patches_tensor.permute(0, 3, 1, 2).unsqueeze(1) # (N, 1, bands, H, W)

    return patches_tensor, (H, W)

# --- Tiling and Inference Functions ---
def process_image_with_tiling(image_path: str, model, pca_model, patch_size=5, tile_size=(100, 100), overlap=10):
    with rasterio.open(image_path) as src:
        img_width = src.width
        img_height = src.height
        num_bands = src.count
        profile = src.profile

        # Prepare output array for classified results
        # Initialize with a placeholder value (e.g., 0 for unlabeled or a background class)
        output_classification = np.zeros((img_height, img_width), dtype=np.uint8)

        # Calculate step size for tiling
        step_x = tile_size[0] - overlap
        step_y = tile_size[1] - overlap

        for i in range(0, img_height, step_y):
            for j in range(0, img_width, step_x):
                # Define window for current tile
                window = Window(j, i, min(tile_size[0], img_width - j), min(tile_size[1], img_height - i))

                # Read tile data
                tile_data = src.read(window=window).astype(np.float32)

                if tile_data.size == 0:
                    continue

                # Preprocess tile and get patches
                patches_tensor, (tile_h, tile_w) = preprocess_tile(tile_data, pca_model, patch_size=patch_size)

                if patches_tensor.nelement() == 0:
                    # No valid patches from this tile, continue to next
                    continue

                # Perform inference
                with torch.no_grad():
                    model_outputs = model(patches_tensor.to(device))
                    _, predicted_classes = torch.max(model_outputs, 1)

                # Reshape predictions back to tile dimensions
                predicted_tile_classes = predicted_classes.cpu().numpy().reshape(tile_h, tile_w)

                # Stitch results into the main output array
                # For overlapping regions, a simple overwrite is used. More sophisticated blending could be added.
                output_classification[i:i+tile_h, j:j+tile_w] = predicted_tile_classes

        return output_classification, profile


# --- FastAPI Application ---
app = FastAPI()

# Request model for prediction
class PredictionRequest(BaseModel):
    image_path: str
    patch_size: int = 5
    tile_width: int = 100
    tile_height: int = 100
    overlap: int = 10

@app.post("/predict")
async def predict_image_tiled(request: PredictionRequest):
    try:
        output_array, profile = process_image_with_tiling(
            request.image_path,
            vit_model,
            pca,
            patch_size=request.patch_size,
            tile_size=(request.tile_width, request.tile_height),
            overlap=request.overlap
        )

        # Save the classified image as a new GeoTIFF
        output_filename = os.path.basename(request.image_path).replace(".tif", "_classified.tif")
        output_path = os.path.join("week4_api_tiling", output_filename)

        profile.update(dtype=rasterio.uint8, count=1) # Classified output has 1 band of uint8 classes

        with rasterio.open(output_path, "w", **profile) as dst:
            dst.write(output_array, 1)

        return {"message": "Classification complete", "output_image_path": output_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok", "model_loaded": True}

