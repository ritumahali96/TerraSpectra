import React, { useEffect, useRef } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

export default function FarmMap() {
  const mapContainerRef = useRef(null);

  useEffect(() => {
    mapboxgl.accessToken = process.env.REACT_APP_MAPBOX_TOKEN || 'pk.eyJ1Ijoicml0dW1haGFsaTk2IiwiYSI6ImNtdG9zazR2djAzOG4yd3NkY2ExNnBhdmoifQ._4seILn1UzctGY0lskXptg';

    const map = new mapboxgl.Map({
      container: mapContainerRef.current,
      style: 'mapbox://styles/mapbox/satellite-v9',
      center: [-121.743, 36.673], // Salinas Valley Farm Center
      zoom: 14.5,
      pitch: 45 // 3D tilt
    });

    // 1. Navigation Controls (Zoom in/out, rotate)
    map.addControl(new mapboxgl.NavigationControl(), 'top-right');

    // 2. Salinas Valley Marker Pin & Popup
    const popup = new mapboxgl.Popup({ closeButton: false, closeOnClick: false, offset: 25 })
      .setHTML('<strong style="color: #0f172a; font-size: 13px;">📍 Salinas Valley Farm</strong><br/><span style="color: #64748b; font-size: 11px;">1,000-Acre Agricultural Test Zone</span>');

    new mapboxgl.Marker({ color: '#22c55e' }) // Green farm marker
      .setLngLat([-121.743, 36.673])
      .setPopup(popup)
      .addTo(map)
      .togglePopup(); // Popup open rahega taaki naam saaf dikhe

    return () => map.remove();
  }, []);

  return (
    <div style={{ position: 'relative', width: '100vw', height: '100vh', margin: 0, padding: 0 }}>
      {/* Mapbox Map Container */}
      <div ref={mapContainerRef} style={{ width: '100%', height: '100%' }} />

      {/* Week 1 Info Badge (Top-Left) */}
      <div
        style={{
          position: 'absolute',
          top: 20,
          left: 20,
          background: 'rgba(15, 23, 42, 0.9)',
          color: 'white',
          padding: '12px 16px',
          borderRadius: '8px',
          fontSize: '13px',
          boxShadow: '0 4px 10px rgba(0,0,0,0.3)',
          zIndex: 10,
          fontFamily: 'sans-serif'
        }}
      >
        <div style={{ fontWeight: 'bold', fontSize: '14px', marginBottom: 4, color: '#4ade80' }}>
          🌱 TerraSpectra — Week 1
        </div>
        <div><strong>Location:</strong> Salinas Valley, California</div>
        <div style={{ fontSize: '11px', color: '#cbd5e1', marginTop: 2 }}>
          Base Geographical Farm Layer (1,000 Acres)
        </div>
      </div>
    </div>
  );
}