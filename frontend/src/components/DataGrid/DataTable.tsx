import React, { useEffect, useState } from 'react';
import { api } from '../../api/client';
import { useData } from '../../context/DataContext';
import { ChevronLeft, ChevronRight, Hash, Type, Calendar, CheckSquare } from 'lucide-react';

export const DataTable: React.FC = () => {
  const { activeSession } = useData();
  const [data, setData] = useState<any[]>([]);
  const [columns, setColumns] = useState<string[]>([]);
  const [colTypes, setColTypes] = useState<Record<string, string>>({});
  const [page, setPage] = useState(1);
  const [pageSize] = useState(50);
  const [totalRows, setTotalRows] = useState(0);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (activeSession) {
      loadPage(1);
    }
  }, [activeSession]);

  const loadPage = async (pageNum: number) => {
    if (!activeSession) return;
    setLoading(true);
    try {
      const res = await api.getPreview(activeSession.session_id, pageNum, pageSize);
      setData(res.data);
      setColumns(res.column_names);
      setColTypes(res.column_types);
      setTotalRows(res.total_rows);
      setPage(pageNum);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (!activeSession) return null;

  const totalPages = Math.ceil(totalRows / pageSize) || 1;

  const getTypeIcon = (dtype: string) => {
    if (dtype.includes('int') || dtype.includes('float')) return <Hash size={14} color="#06b6d4" />;
    if (dtype.includes('date')) return <Calendar size={14} color="#10b981" />;
    return <Type size={14} color="#a855f7" />;
  };

  return (
    <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', height: 'calc(100vh - 120px)' }}>
      {/* Header controls */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
        <div>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#f8fafc' }}>Dataset Explorer</h3>
          <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
            Showing {((page - 1) * pageSize) + 1}–{Math.min(page * pageSize, totalRows)} of {totalRows.toLocaleString()} rows
          </span>
        </div>

        {/* Pagination controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <button
            className="btn btn-secondary btn-sm"
            onClick={() => loadPage(page - 1)}
            disabled={page <= 1 || loading}
          >
            <ChevronLeft size={16} /> Prev
          </button>
          <span style={{ fontSize: '0.85rem', color: '#cbd5e1', fontWeight: 600, padding: '0 0.5rem' }}>
            Page {page} of {totalPages}
          </span>
          <button
            className="btn btn-secondary btn-sm"
            onClick={() => loadPage(page + 1)}
            disabled={page >= totalPages || loading}
          >
            Next <ChevronRight size={16} />
          </button>
        </div>
      </div>

      {/* Grid Container */}
      <div className="custom-table-container" style={{ flex: 1, overflow: 'auto' }}>
        <table className="custom-table">
          <thead>
            <tr>
              <th style={{ width: '50px', textAlign: 'center' }}>#</th>
              {columns.map((col) => (
                <th key={col}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    {getTypeIcon(colTypes[col] || '')}
                    <span>{col}</span>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={columns.length + 1} style={{ textAlign: 'center', padding: '3rem', color: '#94a3b8' }}>
                  Loading page data...
                </td>
              </tr>
            ) : data.length === 0 ? (
              <tr>
                <td colSpan={columns.length + 1} style={{ textAlign: 'center', padding: '3rem', color: '#94a3b8' }}>
                  No rows found.
                </td>
              </tr>
            ) : (
              data.map((row, idx) => (
                <tr key={idx}>
                  <td style={{ textAlign: 'center', color: '#64748b', fontSize: '0.75rem', fontWeight: 600 }}>
                    {((page - 1) * pageSize) + idx + 1}
                  </td>
                  {columns.map((col) => {
                    const val = row[col];
                    const isNull = val === '' || val === null || val === undefined;
                    return (
                      <td key={col} style={{ color: isNull ? '#f43f5e' : 'inherit', fontStyle: isNull ? 'italic' : 'normal' }}>
                        {isNull ? '<null>' : String(val)}
                      </td>
                    );
                  })}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
