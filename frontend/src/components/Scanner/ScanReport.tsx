import React from 'react';
import { useData } from '../../context/DataContext';
import { Activity, AlertTriangle, CheckCircle, HelpCircle, Sparkles, Layers, ArrowRight } from 'lucide-react';

export const ScanReport: React.FC = () => {
  const { scanReport, setActiveTab } = useData();

  if (!scanReport) {
    return (
      <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center', color: '#94a3b8' }}>
        No scan report available.
      </div>
    );
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return '#10b981';
    if (score >= 60) return '#f59e0b';
    return '#f43f5e';
  };

  const scoreColor = getScoreColor(scanReport.quality_score);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }} className="animate-fade-in">
      {/* Top Banner: Score + Summary Stats */}
      <div className="glass-panel glow-card" style={{ padding: '2rem', display: 'grid', gridTemplateColumns: 'auto 1fr', gap: '2.5rem', alignItems: 'center', borderTop: `3px solid ${scoreColor}` }}>
        {/* Animated Quality Score Circular Gauge (Radar style) */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <div 
            className="radar-glow"
            style={{
              position: 'relative', width: '130px', height: '130px', borderRadius: '50%',
              background: `conic-gradient(${scoreColor} ${scanReport.quality_score * 3.6}deg, rgba(255,255,255,0.04) 0deg)`,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              boxShadow: `0 0 35px ${scoreColor}30`
            }}
          >
            {/* Spinning outer cyber-orbit */}
            <div style={{
              position: 'absolute', width: '146px', height: '146px', borderRadius: '50%',
              border: `2px dashed ${scoreColor}50`, animation: 'spin-radar 15s linear infinite',
              pointerEvents: 'none'
            }} />
            <div style={{
              position: 'absolute', width: '154px', height: '154px', borderRadius: '50%',
              border: `1px solid ${scoreColor}20`,
              pointerEvents: 'none'
            }} />
            
            <div style={{
              width: '106px', height: '106px', borderRadius: '50%', background: '#050811',
              display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
              border: '1px solid rgba(255, 255, 255, 0.05)'
            }}>
              <span style={{ fontSize: '2.25rem', fontWeight: 900, color: scoreColor, fontFamily: 'var(--font-mono)', lineHeight: 1 }}>{scanReport.quality_score}</span>
              <span style={{ fontSize: '0.6rem', color: '#94a3b8', fontWeight: 800, letterSpacing: '0.08em', marginTop: '0.2rem' }}>DIAGNOSTIC</span>
            </div>
          </div>
        </div>

        {/* Key Metrics Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem' }}>
          <div style={{ background: 'rgba(5, 8, 17, 0.6)', padding: '1.2rem 1rem', borderRadius: '12px', border: '1px solid rgba(0, 242, 255, 0.15)', boxShadow: 'inset 0 0 10px rgba(0,242,255,0.02)' }}>
            <div style={{ fontSize: '0.72rem', color: '#94a3b8', fontWeight: 700, letterSpacing: '0.05em' }}>TOTAL ROWS</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#f8fafc', marginTop: '0.3rem', fontFamily: 'var(--font-mono)' }}>
              {scanReport.total_rows.toLocaleString()}
            </div>
          </div>

          <div style={{ background: 'rgba(5, 8, 17, 0.6)', padding: '1.2rem 1rem', borderRadius: '12px', border: '1px solid rgba(0, 242, 255, 0.15)', boxShadow: 'inset 0 0 10px rgba(0,242,255,0.02)' }}>
            <div style={{ fontSize: '0.72rem', color: '#94a3b8', fontWeight: 700, letterSpacing: '0.05em' }}>TOTAL COLUMNS</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#f8fafc', marginTop: '0.3rem', fontFamily: 'var(--font-mono)' }}>
              {scanReport.total_columns}
            </div>
          </div>

          <div style={{ background: 'rgba(5, 8, 17, 0.6)', padding: '1.2rem 1rem', borderRadius: '12px', border: '1px solid rgba(0, 242, 255, 0.15)', boxShadow: 'inset 0 0 10px rgba(0,242,255,0.02)' }}>
            <div style={{ fontSize: '0.72rem', color: '#94a3b8', fontWeight: 700, letterSpacing: '0.05em' }}>MISSING CELLS</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: scanReport.missing_percentage > 5 ? 'var(--accent-rose)' : 'var(--accent-emerald)', marginTop: '0.3rem', fontFamily: 'var(--font-mono)' }}>
              {scanReport.missing_cells.toLocaleString()} <span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>({scanReport.missing_percentage}%)</span>
            </div>
          </div>

          <div style={{ background: 'rgba(5, 8, 17, 0.6)', padding: '1.2rem 1rem', borderRadius: '12px', border: '1px solid rgba(0, 242, 255, 0.15)', boxShadow: 'inset 0 0 10px rgba(0,242,255,0.02)' }}>
            <div style={{ fontSize: '0.72rem', color: '#94a3b8', fontWeight: 700, letterSpacing: '0.05em' }}>DUPLICATE ROWS</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: scanReport.duplicate_rows > 0 ? 'var(--accent-amber)' : 'var(--accent-emerald)', marginTop: '0.3rem', fontFamily: 'var(--font-mono)' }}>
              {scanReport.duplicate_rows.toLocaleString()} <span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>({scanReport.duplicate_percentage}%)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Auto Recommendations Section */}
      {scanReport.recommendations.length > 0 && (
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <Sparkles size={20} color="#6366f1" />
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#f8fafc' }}>Auto Purification Recommendations</h3>
            </div>
            <button className="btn btn-primary btn-sm" onClick={() => setActiveTab('clean')}>
              Open Purification Tools <ArrowRight size={16} />
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {scanReport.recommendations.map((rec, idx) => (
              <div key={idx} style={{
                background: 'rgba(15, 23, 42, 0.6)', padding: '0.85rem 1.25rem', borderRadius: '10px',
                borderLeft: `4px solid ${rec.severity === 'high' ? '#f43f5e' : rec.severity === 'medium' ? '#f59e0b' : '#06b6d4'}`,
                display: 'flex', alignItems: 'center', justifyContent: 'space-between'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <AlertTriangle size={18} color={rec.severity === 'high' ? '#f43f5e' : '#f59e0b'} />
                  <span style={{ fontSize: '0.9rem', color: '#e2e8f0' }}>{rec.message}</span>
                </div>
                <span className="badge badge-info" style={{ fontSize: '0.75rem' }}>
                  Action: {rec.suggested_action}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Column Health Profiles Table */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#f8fafc', marginBottom: '1rem' }}>
          Column Profiles & Statistics
        </h3>
        <div className="custom-table-container">
          <table className="custom-table">
            <thead>
              <tr>
                <th>Column Name</th>
                <th>Type</th>
                <th>Null Count</th>
                <th>Null %</th>
                <th>Unique</th>
                <th>Outliers</th>
                <th>Mean / Median</th>
              </tr>
            </thead>
            <tbody>
              {scanReport.columns.map((col) => (
                <tr key={col.name}>
                  <td style={{ fontWeight: 600, color: '#f8fafc' }}>{col.name}</td>
                  <td><span className="badge badge-info" style={{ fontSize: '0.75rem' }}>{col.dtype}</span></td>
                  <td style={{ color: col.null_count > 0 ? '#f43f5e' : 'inherit' }}>{col.null_count}</td>
                  <td>{col.null_percentage}%</td>
                  <td>{col.unique_count}</td>
                  <td style={{ color: (col.outlier_count || 0) > 0 ? '#f59e0b' : 'inherit' }}>
                    {col.outlier_count !== undefined ? col.outlier_count : 'N/A'}
                  </td>
                  <td style={{ color: '#94a3b8' }}>
                    {col.mean !== undefined ? `${col.mean} / ${col.median}` : 'N/A'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
