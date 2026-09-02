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
