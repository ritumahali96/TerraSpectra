# TerraSpectra
Hyperspectral Crop Disease Forecasting
Hyperspectral imaging pipeline for early detection and forecasting of crop diseases using spectral signatures.
## Week 1: Data Processing
Hyperspectral data pipeline for Salinas dataset - loading, normalization, and PCA.

### Dataset
Salinas hyperspectral dataset (512x217 pixels, 204 bands, 16 crop classes).
Source: https://www.ehu.eus/ccwintco/index.php/Hyperspectral_Remote_Sensing_Scenes

### Results
- PCA reduced 204 bands to 15 components (99.95% variance preserved)
- PCA Component 1 visually matches ground truth field boundaries
- Confirms spectral data is well-structured for downstream 3D-CNN + ViT model
