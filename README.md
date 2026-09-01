# TerraSpectra: Hyperspectral Crop Disease Forecasting
Hyperspectral imaging pipeline for early detection and forecasting of crop diseases using spectral signatures.

### Domain: 
Precision Agriculture & Advanced Computer Vision 
### Problem Statement:  
Traditional satellite crop monitoring uses standard RGB or simple infrared imagery. These models only detect crop diseases after the leaves turn yellow or brown, which is too late to save the harvest. Standard 2D Convolutional Neural Networks (CNNs) cannot process the massive depth of data required for early detection. Use Case: An agricultural analyst monitors a 1,000-acre farm via the TerraSpectra dashboard. The system ingests Hyperspectral satellite data (which captures 200+ bands of light, invisible to the human eye). The backend 3D-CNN + Vision Transformer model analyzes the subtle chemical changes in the plants' chlorophyll reflection. The dashboard highlights a specific 5-acre zone in red, predicting a fungal blight outbreak three weeks before any visible symptoms appear on the leaves, allowing for hyper-targeted, preventative pesticide application. 

### Dataset
Salinas hyperspectral dataset (512x217 pixels, 204 bands, 16 crop classes).

Source 1: https://www.ehu.eus/ccwintco/index.php/Hyperspectral_Remote_Sensing_Scenes

Source 2: https://www.kaggle.com/datasets/sreevallimanda/salinas-hyperspectral

### The 16 Salinas Crop/Land Classes with sample counts are: 

Brocoli-green-weeds-1 (2009), Brocoli-green-weeds-2 (3726), Fallow (1976), Fallow-rough-plow (1394), Fallow-smooth (2678), Stubble (3959), Celery (3579), Grapes-untrained (11271), Soil-vineyard-develop (6203), Corn-senesced-green-weeds (3278), Lettuce-romaine-4wk (1068), Lettuce-romaine-5wk (1927), Lettuce-romaine-6wk (916), Lettuce-romaine-7wk (1070), Vinyard-untrained (7268), Vinyard-vertical-trellis (1807), totalling into 54,129 samples.
