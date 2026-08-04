import React from 'react';
import { useData } from '../../context/DataContext';
import { ActiveTab } from '../../types';
import { Upload, Activity, Table, Sparkles, BarChart3, History, Download } from 'lucide-react';

export const Sidebar: React.FC = () => {
  const { activeTab, setActiveTab, activeSession } = useData();

  const navItems: { id: ActiveTab; label: string; icon: React.ReactNode; requiresSession: boolean }[] = [
    { id: 'upload', label: 'Data Source', icon: <Upload size={20} />, requiresSession: false },
    { id: 'scan', label: 'Scan & Health', icon: <Activity size={20} />, requiresSession: true },
    { id: 'grid', label: 'Data Explorer', icon: <Table size={20} />, requiresSession: true },
    { id: 'clean', label: 'Purify Tools', icon: <Sparkles size={20} />, requiresSession: true },
    { id: 'visualize', label: 'Visualizer', icon: <BarChart3 size={20} />, requiresSession: true },
    { id: 'history', label: 'Audit History', icon: <History size={20} />, requiresSession: true },
    { id: 'export', label: 'Export Report', icon: <Download size={20} />, requiresSession: true },
  ];

  return (
    <aside style={{
      width: '240px', background: '#0c1220', borderRight: '1px solid rgba(255, 255, 255, 0.08)',
      display: 'flex', flexDirection: 'column', padding: '1.5rem 1rem', height: '100vh', flexShrink: 0
    }}>
      {/* Brand Logo */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '2.5rem', paddingLeft: '0.5rem' }}>
        <div style={{
          width: '36px', height: '36px', borderRadius: '10px', background: 'linear-gradient(135deg, #6366f1, #06b6d4)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 15px rgba(99, 102, 241, 0.5)'
        }}>
          <Sparkles size={20} color="#ffffff" />
        </div>
        <div>
          <h1 style={{ fontSize: '1.15rem', fontWeight: 800, background: 'linear-gradient(90deg, #ffffff, #cbd5e1)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            DataPurify
          </h1>
          <span style={{ fontSize: '0.68rem', color: '#06b6d4', fontWeight: 600, letterSpacing: '0.05em' }}>PRO ANALYST ENGINE</span>
        </div>
      </div>

      {/* Navigation */}
      <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        {navItems.map((item) => {
          const disabled = item.requiresSession && !activeSession;
          const isActive = activeTab === item.id;

          return (
            <button
              key={item.id}
              onClick={() => !disabled && setActiveTab(item.id)}
              disabled={disabled}
              style={{
                display: 'flex', alignItems: 'center', gap: '0.85rem', padding: '0.75rem 1rem',
                borderRadius: '10px', fontSize: '0.9rem', fontWeight: isActive ? 600 : 500,
                color: isActive ? '#ffffff' : disabled ? '#334155' : '#94a3b8',
                background: isActive ? 'linear-gradient(90deg, rgba(99, 102, 241, 0.2), rgba(99, 102, 241, 0.05))' : 'transparent',
                borderLeft: isActive ? '3px solid #6366f1' : '3px solid transparent',
                border: 'none', cursor: disabled ? 'not-allowed' : 'pointer',
                textAlign: 'left', transition: 'all 0.15s ease'
              }}
            >
              <span style={{ color: isActive ? '#6366f1' : 'inherit' }}>{item.icon}</span>
              {item.label}
            </button>
          );
        })}
      </nav>

      {/* Active Session Card */}
      {activeSession && (
        <div style={{ marginTop: 'auto', padding: '1rem', background: 'rgba(18, 24, 38, 0.6)', borderRadius: '12px', border: '1px solid rgba(255, 255, 255, 0.06)' }}>
          <div style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 600, textTransform: 'uppercase', marginBottom: '0.3rem' }}>Active Session</div>
          <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#f8fafc', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
            {activeSession.filename}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#06b6d4', marginTop: '0.2rem' }}>
            {activeSession.rows.toLocaleString()} rows • {activeSession.columns} cols
          </div>
        </div>
      )}
    </aside>
  );
};
