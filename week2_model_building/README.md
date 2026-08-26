# TerraSpectra - Week 2: 3D-CNN Model Building

## Model Architecture
Custom 3D-CNN with 2 Conv3D layers (8 and 16 filters), dropout (0.4), and 2 fully connected layers.
Input: 5x5x15 hyperspectral patches. Output: 16 crop class predictions.

## Results
- Training Accuracy: 99.68%
- Test Accuracy: 99.69%
- No overfitting observed (train and test accuracy nearly identical)
- Confirms 3D-CNN effectively learns spatial-spectral patterns from hyperspectral patches
