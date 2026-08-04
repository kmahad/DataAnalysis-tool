import React from 'react';
import { useAuth } from '../../context/AuthContext';
import { useData } from '../../context/DataContext';
import { Undo2, Redo2, LogOut, User, Sparkles, AlertCircle } from 'lucide-react';

export const Header: React.FC = () => {
  const { username, logout } = useAuth();
  const { activeSession, scanReport, history, undo, redo, loading, error, setError } = useData();

  return (
    <header style={{
      height: '64px', background: '#090d16', borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
      display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 2rem', flexShrink: 0
    }}>
      {/* Left: Active dataset name and health indicator */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
        {activeSession ? (
          <>
            <div>
              <h2 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#f8fafc' }}>
                {activeSession.filename}
              </h2>
              <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                Session ID: <code style={{ color: '#06b6d4' }}>{activeSession.session_id.substring(0, 8)}</code>
              </div>
            </div>

            {scanReport && (
              <div className="badge badge-info" style={{ gap: '0.4rem', padding: '0.35rem 0.75rem', fontSize: '0.8rem' }}>
                <Sparkles size={14} /> Quality Score: <strong>{scanReport.quality_score}/100</strong>
              </div>
            )}
          </>
        ) : (
          <div style={{ color: '#64748b', fontSize: '0.9rem' }}>No data loaded. Select a data source to begin.</div>
        )}
      </div>

      {/* Center: Global Error Toast if present */}
      {error && (
        <div style={{
          background: 'rgba(244, 63, 94, 0.15)', border: '1px solid rgba(244, 63, 94, 0.3)',
          color: '#f43f5e', padding: '0.4rem 1rem', borderRadius: '8px', fontSize: '0.85rem',
          display: 'flex', alignItems: 'center', gap: '0.5rem'
        }}>
          <AlertCircle size={16} />
          <span>{error}</span>
          <button onClick={() => setError(null)} style={{ background: 'none', border: 'none', color: '#f43f5e', cursor: 'pointer', marginLeft: '0.5rem' }}>✕</button>
        </div>
      )}

      {/* Right: Undo/Redo & User profile */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        {activeSession && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'rgba(255, 255, 255, 0.04)', padding: '0.3rem 0.6rem', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.06)' }}>
            <button
              onClick={() => undo()}
              disabled={!history?.can_undo || loading}
              className="btn btn-secondary btn-sm"
              title="Undo Operation"
              style={{ opacity: history?.can_undo ? 1 : 0.4 }}
            >
              <Undo2 size={16} /> Undo
            </button>
            <button
              onClick={() => redo()}
              disabled={!history?.can_redo || loading}
              className="btn btn-secondary btn-sm"
              title="Redo Operation"
              style={{ opacity: history?.can_redo ? 1 : 0.4 }}
            >
              <Redo2 size={16} /> Redo
            </button>
          </div>
        )}

        <div style={{ width: '1px', height: '24px', background: 'rgba(255, 255, 255, 0.1)' }} />

        {/* User Info */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            width: '34px', height: '34px', borderRadius: '50%', background: 'rgba(99, 102, 241, 0.2)',
            display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#6366f1', border: '1px solid rgba(99, 102, 241, 0.3)'
          }}>
            <User size={18} />
          </div>
          <span style={{ fontSize: '0.875rem', fontWeight: 600, color: '#e2e8f0' }}>{username || 'Analyst'}</span>
          <button
            onClick={logout}
            className="btn btn-secondary btn-sm"
            style={{ padding: '0.4rem', color: '#94a3b8' }}
            title="Logout"
          >
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </header>
  );
};
