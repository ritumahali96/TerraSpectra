import React from 'react';

export default function AnalyticsPanel() {
  return (
    <div
      style={{
        position: 'absolute',
        top: 20,
        right: 20,
        width: '340px',
        maxHeight: '92vh',
        overflowY: 'auto',
        background: 'rgba(15, 23, 42, 0.92)',
        backdropFilter: 'blur(10px)',
        color: '#f8fafc',
        borderRadius: '12px',
        padding: '20px',
        boxShadow: '0 10px 25px rgba(0,0,0,0.5)',
        zIndex: 20,
        fontFamily: 'system-ui, -apple-system, sans-serif'
      }}
    >
      {/* Header */}
      <div style={{ borderBottom: '1px solid #334155', paddingBottom: '12px', marginBottom: '16px' }}>
        <div style={{ fontSize: '11px', color: '#38bdf8', fontWeight: 600, letterSpacing: '0.05em', textTransform: 'uppercase' }}>
          TerraSpectra Intelligence
        </div>
        <h2 style={{ fontSize: '18px', margin: '4px 0 0 0', fontWeight: 700 }}>
          Crop Health Analytics
        </h2>
        <div style={{ fontSize: '12px', color: '#94a3b8' }}>
          Salinas Valley Farm (Sector 4B)
        </div>
      </div>

      {/* Metric 1: Total Acreage at Risk */}
      <div style={{ marginBottom: '20px' }}>
        <div style={{ fontSize: '13px', fontWeight: 600, marginBottom: '10px', color: '#e2e8f0' }}>
          🌾 Acreage Risk Assessment
        </div>

        {/* High Risk Alert Card */}
        <div
          style={{
            background: 'rgba(239, 68, 68, 0.15)',
            border: '1px solid rgba(239, 68, 68, 0.4)',
            borderRadius: '8px',
            padding: '12px',
            marginBottom: '8px'
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '13px', color: '#fca5a5', fontWeight: 600 }}>🚨 Predicted Blight</span>
            <span style={{ fontSize: '18px', fontWeight: 800, color: '#ef4444' }}>5.2 Acres</span>
          </div>
          <div style={{ fontSize: '11px', color: '#f87171', marginTop: '4px' }}>
            Immediate fungicide spray recommended (Target Zone 3)
          </div>
        </div>

        {/* Acreage Breakdown Bars */}
        <div style={{ background: '#1e293b', borderRadius: '8px', padding: '10px', fontSize: '12px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
            <span style={{ color: '#cbd5e1' }}>Mild Chemical Stress:</span>
            <span style={{ fontWeight: 600, color: '#f59e0b' }}>4.8 Acres</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
            <span style={{ color: '#cbd5e1' }}>Optimal / Healthy:</span>
            <span style={{ fontWeight: 600, color: '#22c55e' }}>990.0 Acres</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px solid #334155', paddingTop: '6px' }}>
            <span style={{ color: '#94a3b8' }}>Total Farm Coverage:</span>
            <span style={{ fontWeight: 600, color: '#f8fafc' }}>1,000 Acres</span>
          </div>
        </div>
      </div>

      {/* Metric 2: Chemical Anomalies Detected */}
      <div>
        <div style={{ fontSize: '13px', fontWeight: 600, marginBottom: '10px', color: '#e2e8f0' }}>
          🧪 Spectral Chemical Anomalies
        </div>

        {/* Anomaly 1: Chlorophyll Dip */}
        <div style={{ marginBottom: '10px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '4px' }}>
            <span style={{ color: '#cbd5e1' }}>Chlorophyll A+B Reflection:</span>
            <span style={{ color: '#ef4444', fontWeight: 600 }}>-38.4% (Critical)</span>
          </div>
          <div style={{ width: '100%', height: '6px', background: '#334155', borderRadius: '3px', overflow: 'hidden' }}>
            <div style={{ width: '62%', height: '100%', background: '#ef4444', borderRadius: '3px' }}></div>
          </div>
        </div>

        {/* Anomaly 2: Nitrogen Level */}
        <div style={{ marginBottom: '10px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '4px' }}>
            <span style={{ color: '#cbd5e1' }}>Nitrogen Absorption Index:</span>
            <span style={{ color: '#f59e0b', fontWeight: 600 }}>-21.2% (Moderate)</span>
          </div>
          <div style={{ width: '100%', height: '6px', background: '#334155', borderRadius: '3px', overflow: 'hidden' }}>
            <div style={{ width: '79%', height: '100%', background: '#f59e0b', borderRadius: '3px' }}></div>
          </div>
        </div>

        {/* Anomaly 3: Moisture / Water Index */}
        <div style={{ marginBottom: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '4px' }}>
            <span style={{ color: '#cbd5e1' }}>Cellular Moisture Content:</span>
            <span style={{ color: '#22c55e', fontWeight: 600 }}>Normal (-4.1%)</span>
          </div>
          <div style={{ width: '100%', height: '6px', background: '#334155', borderRadius: '3px', overflow: 'hidden' }}>
            <div style={{ width: '96%', height: '100%', background: '#22c55e', borderRadius: '3px' }}></div>
          </div>
        </div>

        {/* Spectral Curve Mini-Graph (SVG) */}
        <div style={{ background: '#020617', borderRadius: '8px', padding: '12px', border: '1px solid #1e293b' }}>
          <div style={{ fontSize: '11px', color: '#94a3b8', marginBottom: '8px' }}>
            Red-Edge Spectral Shift (680nm - 740nm)
          </div>
          <svg viewBox="0 0 260 60" style={{ width: '100%', height: '60px' }}>
            {/* Healthy Baseline (Green curve) */}
            <path
              d="M 10 50 Q 80 48 130 25 T 250 10"
              fill="none"
              stroke="#22c55e"
              strokeWidth="2"
              strokeDasharray="3 3"
            />
            {/* Blight Anomaly (Red dipped curve) */}
            <path
              d="M 10 50 Q 80 50 130 42 T 250 22"
              fill="none"
              stroke="#ef4444"
              strokeWidth="2.5"
            />
          </svg>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: '#64748b', marginTop: '4px' }}>
            <span>--- Healthy Curve</span>
            <span style={{ color: '#ef4444' }}>— Blight Anomaly</span>
          </div>
        </div>
      </div>
    </div>
  );
}