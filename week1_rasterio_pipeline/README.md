# TerraSpectra - Week 1: Rasterio Data Pipeline

## Approach
Converted the real Salinas hyperspectral cube into GeoTIFF format,
then parsed it using Rasterio (matching the project's satellite raster
format requirement) instead of directly reading the .mat file.

## Why GeoTIFF
GeoTIFF is the standard format for satellite/geospatial raster data
(used by NASA Hyperion, ESA Sentinel). Converting our data into this
format and parsing it with Rasterio validates the pipeline works with
real-world satellite data formats, not just pre-packaged datasets.

## Results
- GeoTIFF successfully created and parsed: 204 bands, EPSG:4326 CRS
- PCA reduced 204 bands to 15 components
- Variance preserved: 99.95%

## Status
Rasterio-based Week 1 pipeline complete. Matches project requirement:
"Use Rasterio to parse hyperspectral data cubes (GeoTIFF format)."
