import React, { useState } from 'react';
import { api } from '../../api/client';
import { useData } from '../../context/DataContext';
import Plot from 'react-plotly.js';
import { BarChart3, LineChart, PieChart, ScatterChart, Activity, Layers } from 'lucide-react';

export const ChartBuilder: React.FC = () => {
  const { scanReport } = useData();
  const [chartType, setChartType] = useState<string>('bar');
  const [xCol, setXCol] = useState<string>('');
  const [yCol, setYCol] = useState<string>('');
  const [colorCol, setColorCol] = useState<string>('');
  const [aggregation, setAggregation] = useState<string>('');
  const [title, setTitle] = useState<string>('');
  const [figJson, setFigJson] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);

  if (!scanReport) return null;

  const cols = scanReport.columns.map((c) => c.name);

  const handleGenerateChart = async () => {
    setLoading(true);
    try {
      const res = await api.generateChart({
        session_id: scanReport.session_id,
        chart_type: chartType,
        x_column: xCol || undefined,
        y_column: yCol || undefined,
        color_column: colorCol || undefined,
        aggregation: aggregation || undefined,
        title: title || undefined,
      });
      setFigJson(res.chart_json);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const chartTypes = [
    { id: 'bar', label: 'Bar Chart', icon: <BarChart3 size={18} /> },
    { id: 'line', label: 'Line Chart', icon: <LineChart size={18} /> },
    { id: 'scatter', label: 'Scatter Plot', icon: <ScatterChart size={18} /> },
    { id: 'pie', label: 'Pie Chart', icon: <PieChart size={18} /> },
    { id: 'histogram', label: 'Histogram', icon: <Activity size={18} /> },
    { id: 'box', label: 'Box Plot', icon: <Layers size={18} /> },
    { id: 'heatmap', label: 'Heatmap', icon: <Layers size={18} /> },
  ];

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: '1.5rem' }}>
      {/* Chart Builder Sidebar */}
      <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#f8fafc' }}>Chart Builder</h3>

        {/* Chart Type Selection */}
        <div>
          <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#cbd5e1', marginBottom: '0.4rem' }}>
            Chart Type
          </label>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.4rem' }}>
            {chartTypes.map((t) => (
              <button
                key={t.id}
                className={`btn ${chartType === t.id ? 'btn-primary' : 'btn-secondary'} btn-sm`}
                onClick={() => setChartType(t.id)}
                style={{ justifyContent: 'flex-start' }}
              >
                {t.icon} {t.label}
              </button>
            ))}
          </div>
        </div>

        {/* X Axis Column */}
        {chartType !== 'heatmap' && (
          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#cbd5e1', marginBottom: '0.4rem' }}>
              X-Axis / Category Column
            </label>
            <select className="select-field" value={xCol} onChange={(e) => setXCol(e.target.value)}>
              <option value="">Select Column</option>
              {cols.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
        )}

        {/* Y Axis Column */}
        {['bar', 'line', 'scatter', 'pie', 'box', 'violin'].includes(chartType) && (
          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#cbd5e1', marginBottom: '0.4rem' }}>
              Y-Axis / Value Column
            </label>
            <select className="select-field" value={yCol} onChange={(e) => setYCol(e.target.value)}>
              <option value="">Select Column</option>
              {cols.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
        )}

        {/* Aggregation */}
        {['bar', 'line'].includes(chartType) && (
          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#cbd5e1', marginBottom: '0.4rem' }}>
              Aggregation
            </label>
            <select className="select-field" value={aggregation} onChange={(e) => setAggregation(e.target.value)}>
              <option value="">None (Raw values)</option>
              <option value="sum">Sum</option>
              <option value="mean">Mean</option>
              <option value="count">Count</option>
              <option value="median">Median</option>
            </select>
          </div>
        )}

        {/* Title */}
        <div>
          <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#cbd5e1', marginBottom: '0.4rem' }}>
            Chart Title (Optional)
          </label>
          <input
            type="text"
            className="input-field"
            placeholder="Custom title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
        </div>

        <button className="btn btn-primary" onClick={handleGenerateChart} disabled={loading} style={{ marginTop: '0.5rem' }}>
          {loading ? 'Rendering...' : 'Generate Visualization'}
        </button>
      </div>

      {/* Chart Render Canvas */}
      <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '500px' }}>
        {figJson ? (
          <Plot
            data={figJson.data}
            layout={{ ...figJson.layout, autosize: true }}
            useResizeHandler={true}
            style={{ width: '100%', height: '100%', minHeight: '480px' }}
            config={{ responsive: true, displayModeBar: true }}
          />
        ) : (
          <div style={{ textAlign: 'center', color: '#64748b' }}>
            <BarChart3 size={48} style={{ opacity: 0.3, marginBottom: '1rem' }} />
            <p>Select parameters on the left and click <strong>Generate Visualization</strong>.</p>
          </div>
        )}
      </div>
    </div>
  );
};
