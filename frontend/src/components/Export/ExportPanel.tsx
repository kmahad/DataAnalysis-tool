import React, { useState } from 'react';
import { api } from '../../api/client';
import { useData } from '../../context/DataContext';
import { Download, FileSpreadsheet, FileText, FileCode } from 'lucide-react';

export const ExportPanel: React.FC = () => {
  const { activeSession } = useData();
  const [format, setFormat] = useState<'csv' | 'excel' | 'html_report'>('csv');
  const [loading, setLoading] = useState(false);

  if (!activeSession) return null;

  const handleExport = async () => {
    setLoading(true);
    try {
      const response = await api.exportData({
        session_id: activeSession.session_id,
        format,
      });

      if (format === 'html_report') {
        const html = await response.text();
        const blob = new Blob([html], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        window.open(url, '_blank');
      } else {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const ext = format === 'excel' ? 'xlsx' : 'csv';
        const baseName = activeSession.filename ? activeSession.filename.split('.')[0] : 'data';
        a.download = `${baseName}_purified.${ext}`;
        document.body.appendChild(a);
        a.click();
        a.remove();
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '2rem', maxWidth: '640px', margin: '0 auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
        <Download size={24} color="#6366f1" />
        <div>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#f8fafc' }}>Export Purified Dataset & Audit Report</h3>
          <p style={{ fontSize: '0.85rem', color: '#94a3b8' }}>Download clean data or export HTML audit summary report</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginBottom: '2rem' }}>
        <div
          onClick={() => setFormat('csv')}
          className="glass-panel glow-card"
          style={{
            padding: '1.5rem', textAlign: 'center', cursor: 'pointer',
            border: `2px solid ${format === 'csv' ? '#6366f1' : 'rgba(255,255,255,0.06)'}`,
            background: format === 'csv' ? 'rgba(99, 102, 241, 0.1)' : 'rgba(15, 23, 42, 0.4)'
          }}
        >
          <FileText size={32} color="#06b6d4" style={{ margin: '0 auto 0.75rem auto', display: 'block' }} />
          <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#f8fafc' }}>CSV Format</h4>
          <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Standard comma separated</span>
        </div>

        <div
          onClick={() => setFormat('excel')}
          className="glass-panel glow-card"
          style={{
            padding: '1.5rem', textAlign: 'center', cursor: 'pointer',
            border: `2px solid ${format === 'excel' ? '#6366f1' : 'rgba(255,255,255,0.06)'}`,
            background: format === 'excel' ? 'rgba(99, 102, 241, 0.1)' : 'rgba(15, 23, 42, 0.4)'
          }}
        >
          <FileSpreadsheet size={32} color="#10b981" style={{ margin: '0 auto 0.75rem auto', display: 'block' }} />
          <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#f8fafc' }}>Excel (.xlsx)</h4>
          <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Formatted spreadsheet</span>
        </div>

        <div
          onClick={() => setFormat('html_report')}
          className="glass-panel glow-card"
          style={{
            padding: '1.5rem', textAlign: 'center', cursor: 'pointer',
            border: `2px solid ${format === 'html_report' ? '#6366f1' : 'rgba(255,255,255,0.06)'}`,
            background: format === 'html_report' ? 'rgba(99, 102, 241, 0.1)' : 'rgba(15, 23, 42, 0.4)'
          }}
        >
          <FileCode size={32} color="#a855f7" style={{ margin: '0 auto 0.75rem auto', display: 'block' }} />
          <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#f8fafc' }}>HTML Audit Report</h4>
          <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Interactive summary report</span>
        </div>
      </div>

      <button className="btn btn-primary" onClick={handleExport} disabled={loading} style={{ width: '100%', padding: '0.85rem' }}>
        <Download size={18} />
        {loading ? 'Generating Export...' : `Download ${format.toUpperCase()}`}
      </button>
    </div>
  );
};
