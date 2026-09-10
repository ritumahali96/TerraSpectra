import React, { useEffect, useRef, useState, useMemo } from 'react';
import mapboxgl from 'mapbox-gl';
import { MapboxOverlay } from '@deck.gl/mapbox';
import { PolygonLayer } from '@deck.gl/layers';
import 'mapbox-gl/dist/mapbox-gl.css';
import AnalyticsPanel from './AnalyticsPanel';

// Satellite Color Mapping: Natural semi-transparent overlay
function getRiskColor(riskScore) {
  if (riskScore >= 0.7) return [239, 68, 68, 175];   // Crimson Red (Blight Outbreak)
  if (riskScore >= 0.45) return [245, 158, 11, 160]; // Amber Orange (Chemical Stress)
  if (riskScore >= 0.3) return [234, 179, 8, 140];   // Yellow (Mild Anomaly)
  return [34, 197, 94, 120];                         // Translucent Green (Healthy)
}

// Generates 144 realistic satellite sensor pixels with organic disease spread
function generateRealisticSatelliteRaster() {
  const cells = [];
  const rows = 12;
  const cols = 12;
  const startLon = -121.748;
  const startLat = 36.669;
  const lonStep = 0.00085;
  const latStep = 0.00065;
  const outbreakLon = -121.7435;
  const outbreakLat = 36.6725;

  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      const minLon = startLon + c * lonStep;
      const maxLon = minLon + lonStep;
      const minLat = startLat + r * latStep;
      const maxLat = minLat + latStep;
      const centerLon = (minLon + maxLon) / 2;
      const centerLat = (minLat + maxLat) / 2;

      // Distance from the biological infection center
      const dist = Math.hypot((centerLon - outbreakLon) * 1.3, centerLat - outbreakLat);
      // Realistic organic spore diffusion falloff
      let risk = Math.exp(-dist * 450) * 0.95;
      risk += Math.sin(r * 2.5 + c * 3.7) * 0.05; // natural irregularity
      risk = Math.max(0.08, Math.min(0.96, risk));

      let status = 'Healthy / Optimal';
      if (risk >= 0.7) status = 'Predicted Fungal Blight';
      else if (risk >= 0.45) status = 'Moderate Chemical Stress';
      else if (risk >= 0.3) status = 'Mild Spectral Drift';

      cells.push({
        id: `pixel-G${r + 1}-${c + 1}`,
        polygon: [
          [minLon, maxLat],
          [maxLon, maxLat],
          [maxLon, minLat],
          [minLon, minLat]
        ],
        riskScore: parseFloat(risk.toFixed(2)),
        status
      });
    }
  }
  return cells;
}

export default function FarmMap() {
  const mapContainerRef = useRef(null);
  const [hoverInfo, setHoverInfo] = useState(null);

  // 144 Realistic Micro-Pixels
  const satelliteGridData = useMemo(() => generateRealisticSatelliteRaster(), []);

  useEffect(() => {
    mapboxgl.accessToken = process.env.REACT_APP_MAPBOX_TOKEN || 'pk.eyJ1Ijoicml0dW1haGFsaTk2IiwiYSI6ImNtdG9zazR2djAzOG4yd3NkY2ExNnBhdmoifQ._4seILn1UzctGY0lskXptg';

    const map = new mapboxgl.Map({
      container: mapContainerRef.current,
      style: 'mapbox://styles/mapbox/satellite-v9',
      center: [-121.743, 36.673], // Salinas Valley Farm Center
      zoom: 14.8,
      pitch: 48 // Cinematic 3D topography tilt
    });

    map.addControl(new mapboxgl.NavigationControl(), 'top-right');

    // High-Resolution Geospatial Raster Overlay
    const overlay = new MapboxOverlay({
      layers: [
        new PolygonLayer({
          id: 'hyperspectral-disease-raster',
          data: satelliteGridData,
          pickable: true,
          stroked: true,
          filled: true,
          lineWidthMinPixels: 0.6,
          getPolygon: (d) => d.polygon,
          getFillColor: (d) => getRiskColor(d.riskScore),
          getLineColor: [255, 255, 255, 50], // Subtle tech sensor border
          onHover: (info) => setHoverInfo(info.object ? info : null)
        })
      ]
    });

    map.addControl(overlay);

    return () => map.remove();
  }, [satelliteGridData]);

  return (
    <div style={{ position: 'relative', width: '100vw', height: '100vh', margin: 0, padding: 0 }}>
      {/* 1. Satellite Base Map */}
      <div ref={mapContainerRef} style={{ width: '100%', height: '100%' }} />

      {/* 2. Analytics Sidebar (Right Side) */}
      <AnalyticsPanel />

      {/* 3. Top-Left System Badge */}
      <div
        style={{
          position: 'absolute',
          top: 20,
          left: 20,
          background: 'rgba(15, 23, 42, 0.92)',
          color: 'white',
          padding: '12px 16px',
          borderRadius: '8px',
          fontSize: '13px',
          boxShadow: '0 4px 12px rgba(0,0,0,0.4)',
          zIndex: 10,
          fontFamily: 'sans-serif'
        }}
      >
        <div style={{ fontWeight: 'bold', fontSize: '14px', marginBottom: 4, color: '#38bdf8' }}>
          🛰️ TerraSpectra — Week 3
        </div>
        <div><strong>Sensor:</strong> Hyperspectral (200+ Bands)</div>
        <div style={{ fontSize: '11px', color: '#94a3b8', marginTop: 2 }}>
          144-Pixel High-Res Raster (Salinas Valley Sector 4B)
        </div>
      </div>

      {/* 4. Hover Tooltip */}
      {hoverInfo && hoverInfo.object && (
        <div
          style={{
            position: 'absolute',
            zIndex: 25,
            pointerEvents: 'none',
            left: hoverInfo.x + 12,
            top: hoverInfo.y + 12,
            background: 'rgba(15, 23, 42, 0.95)',
            color: 'white',
            padding: '8px 12px',
            borderRadius: '6px',
            fontSize: '12px',
            boxShadow: '0 4px 10px rgba(0,0,0,0.5)',
            fontFamily: 'sans-serif',
            border: '1px solid #334155'
          }}
        >
          <div style={{ fontWeight: 600, color: '#38bdf8' }}>{hoverInfo.object.id}</div>
          <div><strong>Status:</strong> {hoverInfo.object.status}</div>
          <div><strong>Disease Risk:</strong> {(hoverInfo.object.riskScore * 100).toFixed(1)}%</div>
        </div>
      )}

      {/* 5. Risk Scale Legend (Bottom-Left) */}
      <div
        style={{
          position: 'absolute',
          bottom: 24,
          left: 24,
          background: 'rgba(15, 23, 42, 0.9)',
          color: 'white',
          padding: '12px 16px',
          borderRadius: '8px',
          fontSize: '12px',
          boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
          zIndex: 10,
          fontFamily: 'sans-serif'
        }}
      >
        <div style={{ fontWeight: 600, marginBottom: 8, color: '#f8fafc' }}>Hyperspectral Risk Index</div>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: 4 }}>
          <span style={{ width: 14, height: 14, background: '#22c55e', marginRight: 8, borderRadius: 2 }}></span>
          Healthy / Optimal (&lt; 30%)
        </div>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: 4 }}>
          <span style={{ width: 14, height: 14, background: '#eab308', marginRight: 8, borderRadius: 2 }}></span>
          Mild Anomaly (30% - 45%)
        </div>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: 4 }}>
          <span style={{ width: 14, height: 14, background: '#f59e0b', marginRight: 8, borderRadius: 2 }}></span>
          Chemical Stress (45% - 70%)
        </div>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <span style={{ width: 14, height: 14, background: '#ef4444', marginRight: 8, borderRadius: 2 }}></span>
          Predicted Blight Outbreak (&gt; 70%)
        </div>
      </div>
    </div>
  );
}