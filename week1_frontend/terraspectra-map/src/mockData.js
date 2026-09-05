export const farmBoundary = {
  type: "Polygon",
  coordinates: [[
    [-121.66, 36.69], [-121.64, 36.69],
    [-121.64, 36.67], [-121.66, 36.67],
    [-121.66, 36.69]
  ]]
};

// Mock zone data - mimics what the trained 3D-CNN model would output
// Each zone represents a small patch of farmland with a predicted crop class
export const mockZones = [
  { id: 1, crop_type: "Grapes untrained", lat: 36.685, lng: -121.655, risk_score: 0.12 },
  { id: 2, crop_type: "Broccoli green weeds", lat: 36.678, lng: -121.648, risk_score: 0.68 },
  { id: 3, crop_type: "Lettuce romaine 5wk", lat: 36.672, lng: -121.642, risk_score: 0.31 },
  { id: 4, crop_type: "Celery", lat: 36.680, lng: -121.660, risk_score: 0.05 }
];
