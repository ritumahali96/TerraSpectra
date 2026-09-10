# TerraSpectra - Week 3: Vision Transformer (ViT) Model for Spectral Attention

## Overview
This folder contains the implementation of a Vision Transformer (ViT) model, specifically tailored for spectral attention, to classify hyperspectral images. It builds upon the data preparation pipeline established in Week 1 (Rasterio parsing and PCA reduction) and Week 2 (patch extraction). The goal is to leverage self-attention mechanisms to learn complex correlations across different light spectrums, aiming for improved classification accuracy.

## Pipeline
1.  **Data Preparation**: Reuses the `create_patches` function from Week 2 to extract spatial patches from the PCA-reduced hyperspectral cube.
2.  **Train/Test Split**: Splits the data into training and testing sets, with stratification to ensure class balance.
3.  **Tensor Conversion**: Converts NumPy arrays to PyTorch tensors and reshapes them to `(batch_size, 1, num_bands, H, W)` for the `SpectralViT` input.
4.  **SpectralViT Model Architecture**:
    *   **MultiHeadSelfAttention**: Custom module for multi-head self-attention.
    *   **TransformerBlock**: Implements a standard Transformer block with multi-head self-attention and an MLP.
    *   **SpectralViT**: The main model, which projects flattened spatial features of each band into an embedding space, adds positional embeddings, and processes them through multiple `TransformerBlock`s to capture inter-band dependencies.
5.  **Training Setup**: Configures `TensorDataset`, `DataLoader`, `CrossEntropyLoss`, and the `Adam` optimizer for model training.
6.  **Training Loop**: Iterates for a specified number of epochs, performing forward passes, calculating loss, backpropagating gradients, and updating model weights.
7.  **Evaluation**: Evaluates the trained `SpectralViT` model on the test set, generating a confusion matrix and a detailed classification report.

## Week 3 Inference
1.  The `SpectralViT` model was trained and evaluated on the Rasterio-derived PCA cube data, achieving a test accuracy of **98.92%**.
2.  The **Confusion Matrix** visually confirms the high accuracy, with most predictions falling along the diagonal, indicating correct classifications for the majority of samples across all classes. (Saved as `results/confusion_matrix.png`)
3.  The **Classification Report** provides a detailed breakdown of the model's performance, showing excellent precision, recall, and F1-scores for nearly all 16 crop classes. This indicates that the `SpectralViT` model is highly effective at distinguishing between different land cover types within the Salinas hyperspectral dataset. (Saved as `results/classification_report.txt`)
4.  The strong performance validates the integration of a self-attention mechanism, demonstrating its effectiveness in capturing complex spectral correlations and fulfilling the Week 3 objective of leveraging advanced architectures for improved accuracy.

## How to Run
1.  Ensure you have run the Week 1 Rasterio pipeline to generate `week1_rasterio_pipeline/cube_pca_rasterio.npy` and `salinas_gt.mat` is accessible at `/TerraSpectra Dataset/salinas_gt.mat`.
2.  Install the required dependencies: `pip install -r requirements.txt`
3.  Execute the Python script: `python spectral_vit_model.py`

## Status
Week 3 SpectralViT model for spectral attention pipeline complete.
