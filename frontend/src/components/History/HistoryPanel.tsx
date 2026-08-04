import React from 'react';
import { useData } from '../../context/DataContext';
import { History, Undo2, Redo2, CheckCircle2, RotateCcw, Clock } from 'lucide-react';

export const HistoryPanel: React.FC = () => {
  const { history, undo, redo, jumpHistory, loading } = useData();

  if (!history || history.entries.length === 0) {
    return (
      <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center', color: '#94a3b8' }}>
        No purification actions recorded yet.
      </div>
    );
  }

  return (
    <div className="glass-panel" style={{ padding: '2rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <History size={24} color="#6366f1" />
          <div>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#f8fafc' }}>Purification Audit Log</h3>
            <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
              Full reproducible history stack ({history.entries.length} states)
            </span>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button className="btn btn-secondary btn-sm" onClick={undo} disabled={!history.can_undo || loading}>
            <Undo2 size={16} /> Undo Step
          </button>
          <button className="btn btn-secondary btn-sm" onClick={redo} disabled={!history.can_redo || loading}>
            <Redo2 size={16} /> Redo Step
          </button>
        </div>
      </div>

      {/* Timeline List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        {history.entries.map((entry) => {
          const isCurrent = entry.index === history.current_index;
          const isFuture = entry.index > history.current_index;

          return (
            <div
              key={entry.index}
              style={{
                background: isCurrent ? 'rgba(99, 102, 241, 0.12)' : 'rgba(15, 23, 42, 0.5)',
                border: `1px solid ${isCurrent ? '#6366f1' : 'rgba(255, 255, 255, 0.06)'}`,
                opacity: isFuture ? 0.45 : 1,
                borderRadius: '12px', padding: '1rem 1.25rem',
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                transition: 'all 0.15s ease'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <div style={{
                  width: '32px', height: '32px', borderRadius: '50%',
                  background: isCurrent ? '#6366f1' : 'rgba(255, 255, 255, 0.06)',
                  color: isCurrent ? '#fff' : '#94a3b8',
                  display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.85rem', fontWeight: 700
                }}>
                  {entry.index}
                </div>

                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span style={{ fontWeight: 700, color: '#f8fafc', fontSize: '0.95rem' }}>
                      {entry.operation}
                    </span>
                    {isCurrent && <span className="badge badge-success" style={{ fontSize: '0.7rem' }}>CURRENT STATE</span>}
                    {isFuture && <span className="badge badge-warning" style={{ fontSize: '0.7rem' }}>UNDONE</span>}
                  </div>
                  <p style={{ fontSize: '0.85rem', color: '#cbd5e1', marginTop: '0.1rem' }}>{entry.description}</p>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <div style={{ textAlign: 'right', fontSize: '0.75rem', color: '#64748b' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                    <Clock size={12} /> {new Date(entry.timestamp).toLocaleTimeString()}
                  </div>
                  <div>Rows Affected: {entry.rows_affected}</div>
                </div>

                {!isCurrent && (
                  <button
                    className="btn btn-secondary btn-sm"
                    onClick={() => jumpHistory(entry.index)}
                    disabled={loading}
                  >
                    <RotateCcw size={14} /> Jump Here
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
