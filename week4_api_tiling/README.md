# TerraSpectra - Week 4: API & Tiling

## Overview
This week's objective focuses on deploying the trained hyperspectral image classification model as a web API using FastAPI and implementing a robust tiling algorithm to handle large satellite images. The API will accept GeoTIFF images, process them in chunks (tiles), perform inference using the PCA and SpectralViT models, and return a classified GeoTIFF.

## Contents
- `main.py`: Contains the FastAPI application, model loading, preprocessing logic, tiling algorithm, and API endpoints.
- `pca_model.joblib`: The saved PCA model from Week 1, used for dimensionality reduction.
- `spectral_vit_model_state_dict.pth`: The saved state dictionary of the trained SpectralViT model from Week 3.

## Pipeline
1.  **Model Saving**: The trained PCA model and SpectralViT model's state dictionary are saved for deployment.
2.  **FastAPI Application (`main.py`)**:
    -   Loads `pca_model.joblib` and `spectral_vit_model_state_dict.pth`.
    -   Implements `normalize_band` and `preprocess_tile` functions to prepare image tiles for inference.
    -   `process_image_with_tiling` handles reading large GeoTIFFs, splitting them into overlapping tiles, performing per-tile inference, and stitching the results.
    -   Defines a `/predict` endpoint to trigger the classification of an input image path with configurable tiling parameters.
    -   Includes a `/health` endpoint for basic service checks.

## How to Run the API (Conceptual in Colab)
1.  **Ensure Models Exist**: Make sure `pca_model.joblib` and `spectral_vit_model_state_dict.pth` are present in the `week4_api_tiling` directory.
2.  **Run Uvicorn (simulated in Colab)**:
    ```bash
    # This command would be run in a terminal to start the FastAPI server
    # !uvicorn week4_api_tiling.main:app --host 0.0.0.0 --port 8000
    ```
    In Colab, you might need to use `nest_asyncio` and run `uvicorn` programmatically or use `ngrok` for external access.
3.  **Send a Prediction Request (Example)**:
    ```python
    import requests
    import json

    # Replace with the actual URL if using ngrok or a deployed service
    api_url = "http://127.0.0.1:8000/predict"

    # Example: you would first upload your input GeoTIFF to the Colab environment
    # or ensure it's accessible via a path the API can read.
    # For this example, we assume 'salinas_hyperspectral.tif' is available in /content/TerraSpectra
    payload = {
        "image_path": "salinas_hyperspectral.tif", # Path relative to where the API runs
        "patch_size": 5,
        "tile_width": 100,
        "tile_height": 100,
        "overlap": 10
    }

    headers = {'Content-Type': 'application/json'}

    # response = requests.post(api_url, data=json.dumps(payload), headers=headers)
    # print(response.json())
    ```

## Status
Week 4 API & Tiling implementation complete.
