# TerraSpectra - Week 2: 3D-CNN Model Training

## Overview
This folder contains the implementation of a 3D-CNN model for hyperspectral image classification, building upon the data pipeline established in Week 1. The data (PCA-reduced cube and ground truth labels) is assumed to be prepared by the Week 1 Rasterio pipeline.

## Pipeline
1.  **Data Preparation**: Patches are extracted from the PCA-reduced hyperspectral cube, and corresponding ground truth labels are prepared.
2.  **Train/Test Split**: Data is split into training and testing sets, ensuring stratified sampling.
3.  **Tensor Conversion**: NumPy arrays are converted to PyTorch tensors and reshaped for 3D-CNN input.
4.  **3D-CNN Architecture**: A `Simple3DCNN` model is defined, consisting of convolutional, dropout, and fully connected layers.
5.  **Training Setup**: `TensorDataset`, `DataLoader`, `CrossEntropyLoss`, and `Adam` optimizer are configured.
6.  **Training Loop**: The model is trained over multiple epochs, with loss and accuracy tracked.
7.  **Evaluation**: The trained model is evaluated on the test set to determine its performance.

## Week 2 Inference
- The 3D-CNN model was retrained using the Rasterio-derived PCA cube.
- Achieved high training and test accuracies (e.g., ~99.6% training, ~99.7% test accuracy), demonstrating consistent performance with the original pipeline.
- This validates a robust, fully consistent, Rasterio-based Week 1 + Week 2 ML pipeline, capable of handling real-world satellite raster formats (GeoTIFF) with comparable accuracy to pre-packaged datasets.

## Status
Week 2 Rasterio-based 3D-CNN model training pipeline complete.
