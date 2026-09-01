import React from 'react';
import DeckGL from '@deck.gl/react';
import { StaticMap } from 'react-map-gl';
import { GeoJsonLayer } from '@deck.gl/layers';
import { MAPBOX_TOKEN } from './config';
import { farmBoundary } from './mockData';

function FarmMap() {
  return (
    <div style={{ width: '100%', height: '500px' }}>
      <DeckGL
        initialViewState={INITIAL_VIEW_STATE}
        controller={true}
        layers={[farmLayer]}
      >
        <StaticMap mapboxApiAccessToken={MAPBOX_TOKEN} />
      </DeckGL>
    </div>
  );
}

export default FarmMap;

const INITIAL_VIEW_STATE = {
  longitude: -121.65,
  latitude: 36.68,
  zoom: 13,
  pitch: 0,
  bearing: 0
};

const farmLayer = new GeoJsonLayer({
  id: 'farm-boundary',
  data: farmBoundary,
  filled: true,
  getFillColor: [44, 95, 45, 100],
  getLineColor: [151, 188, 98],
  lineWidthMinPixels: 2
});
