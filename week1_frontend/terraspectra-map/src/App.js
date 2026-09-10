import React from 'react';
import FarmMap from './components/FarmMap';

function App() {
  return (
    <div style={{ width: '100vw', height: '100vh', background: '#f0fdf4' }}>
      <h2 style={{ position: 'absolute', top: 10, left: 10, zIndex: 999, color: 'black' }}>
        🚜 TerraSpectra Map Loading...
      </h2>
      <FarmMap />
    </div>
  );
}

export default App;