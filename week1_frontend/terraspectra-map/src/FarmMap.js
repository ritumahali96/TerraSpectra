import React from 'react';
import DeckGL from '@deck.gl/react';
import { StaticMap } from 'react-map-gl';
import { GeoJsonLayer } from '@deck.gl/layers';
import { MAPBOX_TOKEN } from './config';
import { farmBoundary } from './mockData';

function FarmMap() {
  return <div id="map-container" style={{ width: '100%', height: '500px' }}></div>;
}

export default FarmMap;

const INITIAL_VIEW_STATE = {
  longitude: -121.65,
  latitude: 36.68,
  zoom: 13,
  pitch: 0,
  bearing: 0
};
