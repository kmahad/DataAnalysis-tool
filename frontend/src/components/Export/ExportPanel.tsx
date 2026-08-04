import React, { useState } from 'react';
import { api } from '../../api/client';
import { useData } from '../../context/DataContext';
import { Download, FileSpreadsheet, FileText, FileCode, Presentation } from 'lucide-react';

export const ExportPanel: React.FC = () => {
  const { activeSession } = useData();
  const [format, setFormat] = useState<'csv' | 'excel' | 'html_report' | 'powerpoint'>('csv');
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
        const extMap: Record<string, string> = {
          csv: 'csv',
          excel: 'xlsx',
          powerpoint: 'pptx',
        };
        const ext = extMap[format] || format;
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

  const formatOptions = [
    {
      id: 'csv' as const,
      label: 'CSV Format',
      description: 'Standard comma separated',
      icon: <FileText size={32} color="#06b6d4" style={{ margin: '0 auto 0.75rem auto', display: 'block' }} />,
    },
    {
      id: 'excel' as const,
      label: 'Excel (.xlsx)',
      description: 'Formatted spreadsheet',
      icon: <FileSpreadsheet size={32} color="#10b981" style={{ margin: '0 auto 0.75rem auto', display: 'block' }} />,
    },
    {
      id: 'html_report' as const,
      label: 'HTML Audit Report',
      description: 'Interactive summary report',
      icon: <FileCode size={32} color="#a855f7" style={{ margin: '0 auto 0.75rem auto', display: 'block' }} />,
    },
    {
      id: 'powerpoint' as const,
      label: 'PowerPoint (.pptx)',
      description: 'Visual summary with charts & insights',
      icon: <Presentation size={32} color="#f59e0b" style={{ margin: '0 auto 0.75rem auto', display: 'block' }} />,
    },
  ];

  return (
    <div className="glass-panel" style={{ padding: '2rem', maxWidth: '720px', margin: '0 auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
        <Download size={24} color="#6366f1" />
        <div>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#f8fafc' }}>Export Purified Dataset & Audit Report</h3>
          <p style={{ fontSize: '0.85rem', color: '#94a3b8' }}>Download clean data, audit reports, or visual presentation summaries</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '2rem' }}>
        {formatOptions.map((opt) => (
          <div
            key={opt.id}
            onClick={() => setFormat(opt.id)}
            className="glass-panel glow-card"
            style={{
              padding: '1.5rem', textAlign: 'center', cursor: 'pointer',
              border: `2px solid ${format === opt.id ? '#6366f1' : 'rgba(255,255,255,0.06)'}`,
              background: format === opt.id ? 'rgba(99, 102, 241, 0.1)' : 'rgba(15, 23, 42, 0.4)'
            }}
          >
            {opt.icon}
            <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#f8fafc' }}>{opt.label}</h4>
            <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>{opt.description}</span>
          </div>
        ))}
      </div>

      <button className="btn btn-primary" onClick={handleExport} disabled={loading} style={{ width: '100%', padding: '0.85rem' }}>
        <Download size={18} />
        {loading ? 'Generating Export...' : `Download ${format.toUpperCase()}`}
      </button>
    </div>
  );
};
