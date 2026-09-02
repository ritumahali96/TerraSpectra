# TerraSpectra - Week 1: Frontend & GIS Dashboard

## Setup
1. cd terraspectra-map
2. npm install
3. Add your Mapbox token in src/config.js
4. npm start

## What This Does
Renders a base map centered on the Salinas Valley farm (matching the same
coordinates used in the Week 1 ML Rasterio pipeline), with the farm boundary
overlaid as a Deck.gl GeoJsonLayer on top of a Mapbox base map.

Mock zone data reflects the same crop classes and risk-score structure that
the trained 3D-CNN model (Week 2 ML) will eventually output via the Week 4
FastAPI backend.

## Architecture Note
Frontend and ML backend are developed independently in Week 1-2, using mock
data with the same structure the real model will produce. They will be
connected via the FastAPI inference endpoint in Week 4.

## Results
- React app scaffolded successfully
- Deck.gl + Mapbox integrated, rendering base map
- Farm boundary layer overlaid on Salinas Valley coordinates
- Mock zone data structured to match future model output

## Next (Week 2)
Overlay disease-risk heatmap grid using the mock zone data, with color-coded
risk levels rendered on top of the base map.

## Status
Week 1 Frontend Complete. Base map, farm boundary, and mock zone data ready.

## Running the Dashboard
1. Get a free Mapbox token from mapbox.com
2. Paste it in `terraspectra-map/src/config.js`
3. `cd terraspectra-map && npm install && npm start`
