import React, { useState } from 'react';
import { api } from '../../api/client';
import { useData } from '../../context/DataContext';
import { Database, Server, Play, ListFilter, AlertCircle } from 'lucide-react';

export const DatabaseConnect: React.FC = () => {
  const [dbType, setDbType] = useState<'postgresql' | 'mysql' | 'sqlite'>('postgresql');
  const [connStr, setConnStr] = useState('');
  const [tables, setTables] = useState<string[]>([]);
  const [selectedTable, setSelectedTable] = useState('');
  const [customQuery, setCustomQuery] = useState('');
  const [mode, setMode] = useState<'table' | 'query'>('table');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { setSession } = useData();

  const handleTestConnection = async () => {
    if (!connStr) {
      setError('Please provide a valid database connection string');
      return;
    }
    setError(null);
    setLoading(true);
    try {
      const res = await api.getDatabaseTables({ db_type: dbType, connection_string: connStr });
      setTables(res.tables);
      if (res.tables.length > 0) setSelectedTable(res.tables[0]);
    } catch (err: any) {
      setError(err.message || 'Failed to connect to database');
    } finally {
      setLoading(false);
    }
  };

  const handleLoadData = async () => {
    setError(null);
    setLoading(true);
    try {
      const res = await api.connectDatabase({
        db_type: dbType,
        connection_string: connStr,
        table_name: mode === 'table' ? selectedTable : undefined,
        query: mode === 'query' ? customQuery : undefined,
      });
      setSession(res);
    } catch (err: any) {
      setError(err.message || 'Failed to load database data');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '2rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
        <Database size={24} color="#6366f1" />
        <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#f8fafc' }}>
          Connect to Cloud / SQL Database
        </h3>
      </div>

      {error && (
        <div style={{ marginBottom: '1.5rem', padding: '0.75rem', background: 'rgba(244, 63, 94, 0.15)', border: '1px solid rgba(244, 63, 94, 0.3)', borderRadius: '8px', color: '#f43f5e', fontSize: '0.875rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <AlertCircle size={16} /> {error}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '1.5rem', marginBottom: '1.5rem' }}>
        <div>
          <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#cbd5e1', marginBottom: '0.4rem' }}>
            Database Engine
          </label>
          <select className="select-field" value={dbType} onChange={(e: any) => setDbType(e.target.value)}>
            <option value="postgresql">PostgreSQL (Supabase / AWS RDS)</option>
            <option value="mysql">MySQL / MariaDB (PlanetScale)</option>
            <option value="sqlite">SQLite File</option>
          </select>
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#cbd5e1', marginBottom: '0.4rem' }}>
            Connection String
          </label>
          <input
            type="text"
            className="input-field"
            placeholder={dbType === 'postgresql' ? 'postgresql://user:pass@host:5432/dbname' : 'mysql+pymysql://user:pass@host:3306/dbname'}
            value={connStr}
            onChange={(e) => setConnStr(e.target.value)}
          />
        </div>
      </div>

      <button className="btn btn-secondary" onClick={handleTestConnection} disabled={loading} style={{ marginBottom: '1.5rem' }}>
        <Server size={16} /> {loading ? 'Connecting...' : 'Test Connection & Fetch Tables'}
      </button>

      {tables.length > 0 && (
        <div className="animate-fade-in" style={{ borderTop: '1px solid rgba(255, 255, 255, 0.08)', paddingTop: '1.5rem' }}>
          <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
            <button className={`btn ${mode === 'table' ? 'btn-primary' : 'btn-secondary'} btn-sm`} onClick={() => setMode('table')}>
              <ListFilter size={16} /> Select Table
            </button>
            <button className={`btn ${mode === 'query' ? 'btn-primary' : 'btn-secondary'} btn-sm`} onClick={() => setMode('query')}>
              <Play size={16} /> Custom SQL Query
            </button>
          </div>

          {mode === 'table' ? (
            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#cbd5e1', marginBottom: '0.4rem' }}>
                Select Table ({tables.length} available)
              </label>
              <select className="select-field" value={selectedTable} onChange={(e) => setSelectedTable(e.target.value)}>
                {tables.map((t) => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
            </div>
          ) : (
            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#cbd5e1', marginBottom: '0.4rem' }}>
                SQL Query
              </label>
              <textarea
                className="input-field"
                rows={4}
                style={{ fontFamily: 'monospace' }}
                placeholder="SELECT * FROM sales WHERE amount > 1000"
                value={customQuery}
                onChange={(e) => setCustomQuery(e.target.value)}
              />
            </div>
          )}

          <button className="btn btn-primary" onClick={handleLoadData} disabled={loading}>
            <Database size={16} /> {loading ? 'Loading Data...' : 'Import Data into Session'}
          </button>
        </div>
      )}
    </div>
  );
};
