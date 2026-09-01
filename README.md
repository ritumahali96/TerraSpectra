# TerraSpectra
Hyperspectral Crop Disease Forecasting
Hyperspectral imaging pipeline for early detection and forecasting of crop diseases using spectral signatures.
## Week 1: Data Processing
Hyperspectral data pipeline for Salinas dataset - loading, normalization, and PCA.

### Dataset
Salinas hyperspectral dataset (512x217 pixels, 204 bands, 16 crop classes).
Source: https://www.ehu.eus/ccwintco/index.php/Hyperspectral_Remote_Sensing_Scenes

The 16 Salinas Crop/Land Classes:

with sample counts are: Brocoli-green-weeds-1 (2009), Brocoli-green-weeds-2 (3726), Fallow (1976), Fallow-rough-plow (1394), Fallow-smooth (2678), Stubble (3959), Celery (3579), Grapes-untrained (11271), Soil-vineyard-develop (6203), Corn-senesced-green-weeds (3278), Lettuce-romaine-4wk (1068), Lettuce-romaine-5wk (1927), Lettuce-romaine-6wk (916), Lettuce-romaine-7wk (1070), Vinyard-untrained (7268), and Vinyard-vertical-trellis (1807), totaling 54,129 samples

### Results
- PCA reduced 204 bands to 15 components (99.95% variance preserved)
- PCA Component 1 visually matches ground truth field boundaries
- Confirms spectral data is well-structured for downstream 3D-CNN + ViT model

### Status
Week 1 Complete. Data pipeline validated on real Salinas hyperspectral dataset.

## TerraSpectra - Week 2: 3D-CNN Model Building
### Model Architecture
Custom 3D-CNN with 2 Conv3D layers (8 and 16 filters), dropout (0.4), and 2 fully connected layers. Input: 5x5x15 hyperspectral patches. Output: 16 crop class predictions.

### Results
Training Accuracy: 99.68%
Test Accuracy: 99.69%
No overfitting observed (train and test accuracy nearly identical)
Confirms 3D-CNN effectively learns spatial-spectral patterns from hyperspectral patches
Status
Week 2 Complete. 3D-CNN model successfully trained and validated on Salinas dataset. Next: Integrate Vision Transformer (ViT) for Week 3.
