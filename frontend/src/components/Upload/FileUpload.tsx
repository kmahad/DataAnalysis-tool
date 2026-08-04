import React, { useState } from 'react';
import { api } from '../../api/client';
import { useData } from '../../context/DataContext';
import { UploadCloud, FileSpreadsheet, CheckCircle2, AlertCircle } from 'lucide-react';

export const FileUpload: React.FC = () => {
  const [dragActive, setDragActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { setSession } = useData();

  const handleFile = async (file: File) => {
    if (!file.name.match(/\.(csv|xlsx|xls)$/i)) {
      setError('Please upload a valid CSV or Excel file (.csv, .xlsx, .xls)');
      return;
    }

    setError(null);
    setLoading(true);

    try {
      const res = await api.uploadFile(file);
      setSession(res);
    } catch (err: any) {
      setError(err.message || 'File upload failed');
    } finally {
      setLoading(false);
    }
  };

  const onDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(true);
  };

  const onDragLeave = () => setDragActive(false);

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className="glass-panel glow-card" style={{ padding: '3rem 2rem', textAlign: 'center' }}>
      <div
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        style={{
          border: `2px dashed ${dragActive ? '#6366f1' : 'rgba(255, 255, 255, 0.15)'}`,
          borderRadius: '16px', padding: '3.5rem 2rem', background: dragActive ? 'rgba(99, 102, 241, 0.05)' : 'rgba(15, 23, 42, 0.4)',
          transition: 'all 0.2s ease', cursor: 'pointer'
        }}
      >
        <div style={{
          width: '64px', height: '64px', borderRadius: '50%', background: 'rgba(99, 102, 241, 0.15)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1.5rem auto', color: '#6366f1'
        }}>
          <UploadCloud size={36} />
        </div>

        <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#f8fafc', marginBottom: '0.5rem' }}>
          Drag & Drop your Data File here
        </h3>
        <p style={{ color: '#94a3b8', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
          Supports <strong>CSV</strong>, <strong>Excel (.xlsx)</strong> files up to 500MB
        </p>

        <label className="btn btn-primary" style={{ cursor: 'pointer' }}>
          <FileSpreadsheet size={18} />
          {loading ? 'Uploading & Parsing...' : 'Browse Computer'}
          <input
            type="file"
            accept=".csv, .xlsx, .xls"
            style={{ display: 'none' }}
            onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
            disabled={loading}
          />
        </label>
      </div>

      {error && (
        <div style={{ marginTop: '1.5rem', padding: '0.75rem', background: 'rgba(244, 63, 94, 0.15)', border: '1px solid rgba(244, 63, 94, 0.3)', borderRadius: '8px', color: '#f43f5e', fontSize: '0.875rem', display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}>
          <AlertCircle size={16} />
          {error}
        </div>
      )}
    </div>
  );
};
