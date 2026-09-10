import React, { useEffect, useRef, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import { MapboxOverlay } from '@deck.gl/mapbox';
import { PolygonLayer } from '@deck.gl/layers';
import 'mapbox-gl/dist/mapbox-gl.css';
import mockData from '../data/mockFarmData.json';

// Color rule: Green for healthy, Yellow for mild, Red for outbreak
function getRiskColor(riskScore) {
  if (riskScore >= 0.7) return [239, 68, 68, 180];  // Red
  if (riskScore >= 0.4) return [245, 158, 11, 180]; // Orange/Yellow
  return [34, 197, 94, 180];                       // Green
}

export default function FarmMap() {
  const mapContainerRef = useRef(null);
  const [hoverInfo, setHoverInfo] = useState(null);

  useEffect(() => {
    // ⚠️ Yahan apna Week 1 wala Mapbox token paste karein
    mapboxgl.accessToken = process.env.REACT_APP_MAPBOX_TOKEN || 'pk.eyJ1Ijoicml0dW1haGFsaTk2IiwiYSI6ImNtdG9zazR2djAzOG4yd3NkY2ExNnBhdmoifQ._4seILn1UzctGY0lskXptg';

    const map = new mapboxgl.Map({
      container: mapContainerRef.current,
      style: 'mapbox://styles/mapbox/satellite-v9',
      center: [-121.743, 36.673], // Farm Center
      zoom: 15,
      pitch: 45 // 3D tilt
    });

    // Deck.gl Heatmap Grid Layer
    const overlay = new MapboxOverlay({
      layers: [
        new PolygonLayer({
          id: 'crop-disease-heatmap',
          data: mockData,
          pickable: true,
          stroked: true,
          filled: true,
          lineWidthMinPixels: 1,
          getPolygon: (d) => d.polygon,
          getFillColor: (d) => getRiskColor(d.riskScore),
          getLineColor: [255, 255, 255, 200],
          onHover: (info) => setHoverInfo(info.object ? info : null)
        })
      ]
    });

    map.addControl(overlay);

    return () => map.remove();
  }, []);

  return (
    <div style={{ position: 'relative', width: '100vw', height: '100vh' }}>
      {/* Real Mapbox Container */}
      <div ref={mapContainerRef} style={{ width: '100%', height: '100%' }} />

      {/* Tooltip on Hover */}
      {hoverInfo && hoverInfo.object && (
        <div
          style={{
            position: 'absolute',
            zIndex: 10,
            pointerEvents: 'none',
            left: hoverInfo.x + 12,
            top: hoverInfo.y + 12,
            background: 'rgba(15, 23, 42, 0.9)',
            color: 'white',
            padding: '8px 12px',
            borderRadius: '6px',
            fontSize: '12px'
          }}
        >
          <div><strong>Status:</strong> {hoverInfo.object.status}</div>
          <div><strong>Risk:</strong> {(hoverInfo.object.riskScore * 100).toFixed(0)}%</div>
          <div><strong>Cell ID:</strong> {hoverInfo.object.id}</div>
        </div>
      )}

      {/* Legend */}
      <div
        style={{
          position: 'absolute',
          bottom: 24,
          right: 24,
          background: 'rgba(255, 255, 255, 0.95)',
          padding: '12px 16px',
          borderRadius: '8px',
          fontSize: '13px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
          zIndex: 5
        }}
      >
        <div style={{ fontWeight: 600, marginBottom: 8 }}>Crop Disease Risk</div>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: 4 }}>
          <span style={{ width: 14, height: 14, background: '#22c55e', marginRight: 8, borderRadius: 2 }}></span>
          Healthy (&lt; 40%)
        </div>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: 4 }}>
          <span style={{ width: 14, height: 14, background: '#f59e0b', marginRight: 8, borderRadius: 2 }}></span>
          Mild Stress (40% - 70%)
        </div>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <span style={{ width: 14, height: 14, background: '#ef4444', marginRight: 8, borderRadius: 2 }}></span>
          Predicted Blight (&gt; 70%)
        </div>
      </div>
    </div>
  );
}