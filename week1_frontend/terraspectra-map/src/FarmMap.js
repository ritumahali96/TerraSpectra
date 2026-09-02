import React, { useEffect, useRef } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { MapboxOverlay } from '@deck.gl/mapbox';
import { GeoJsonLayer } from '@deck.gl/layers';
import { MAPBOX_TOKEN } from './config';
import { farmBoundary } from './mockData';

mapboxgl.accessToken = MAPBOX_TOKEN;

function FarmMap() {
  const mapContainer = useRef(null);
  const mapRef = useRef(null);

  useEffect(() => {
    if (mapRef.current) return; // prevent re-initializing

    const map = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/satellite-streets-v11',
      center: [-121.65, 36.68],
      zoom: 13
    });

    const farmLayer = new GeoJsonLayer({
      id: 'farm-boundary',
      data: farmBoundary,
      filled: true,
      getFillColor: [44, 95, 45, 100],
      getLineColor: [151, 188, 98],
      lineWidthMinPixels: 2
    });

    const overlay = new MapboxOverlay({ layers: [farmLayer] });
    map.addControl(overlay);

    mapRef.current = map;
  }, []);

  return <div ref={mapContainer} style={{ width: '100%', height: '500px' }} />;
}

export default FarmMap;
