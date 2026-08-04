import React, { useState } from 'react';
import { api } from '../../api/client';
import { useData } from '../../context/DataContext';
import { Sparkles, Trash2, CopyX, Activity, Type, List, CheckCircle2 } from 'lucide-react';

export const CleaningPanel: React.FC = () => {
  const { activeSession, scanReport, refreshScanReport, refreshHistory, setError } = useData();
  const [activeTool, setActiveTool] = useState<'missing' | 'duplicates' | 'outliers' | 'types' | 'strings' | 'columns'>('missing');
  const [loading, setLoading] = useState(false);

  // Missing values state
  const [selectedCols, setSelectedCols] = useState<string[]>([]);
  const [missingStrategy, setMissingStrategy] = useState<string>('drop_rows');
  const [fillValue, setFillValue] = useState<string>('');

  // Duplicates state
  const [keepStrategy, setKeepStrategy] = useState<string>('first');

  // Outliers state
  const [outlierMethod, setOutlierMethod] = useState<string>('iqr');
  const [outlierAction, setOutlierAction] = useState<string>('remove');
  const [outlierThreshold, setOutlierThreshold] = useState<number>(1.5);

  // Strings state
  const [stringActions, setStringActions] = useState<string[]>(['trim']);

  if (!activeSession || !scanReport) return null;

  const columnNames = scanReport.columns.map((c) => c.name);

  const toggleColumnSelection = (col: string) => {
    setSelectedCols((prev) =>
      prev.includes(col) ? prev.filter((c) => c !== col) : [...prev, col]
    );
  };

  const selectAllColumns = () => setSelectedCols(columnNames);
  const clearColumnSelection = () => setSelectedCols([]);

  const handleApplyMissing = async () => {
    if (selectedCols.length === 0) {
      setError('Please select at least one column');
      return;
    }
    setLoading(true);
    try {
      await api.cleanMissing({
        session_id: activeSession.session_id,
        columns: selectedCols,
        strategy: missingStrategy,
        fill_value: fillValue || undefined,
      });
      await refreshScanReport();
      await refreshHistory();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleApplyDuplicates = async () => {
    setLoading(true);
    try {
      await api.cleanDuplicates({
        session_id: activeSession.session_id,
        subset_columns: selectedCols.length > 0 ? selectedCols : undefined,
        keep: keepStrategy,
      });
      await refreshScanReport();
      await refreshHistory();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleApplyOutliers = async () => {
    if (selectedCols.length === 0) {
      setError('Please select at least one numeric column');
      return;
    }
    setLoading(true);
    try {
      await api.cleanOutliers({
        session_id: activeSession.session_id,
        columns: selectedCols,
        method: outlierMethod,
        action: outlierAction,
        threshold: outlierThreshold,
      });
      await refreshScanReport();
      await refreshHistory();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleApplyStrings = async () => {
    if (selectedCols.length === 0) {
      setError('Please select at least one column');
      return;
    }
    setLoading(true);
    try {
      await api.cleanStrings({
        session_id: activeSession.session_id,
        columns: selectedCols,
        actions: stringActions,
      });
      await refreshScanReport();
      await refreshHistory();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '260px 1fr', gap: '1.5rem' }}>
      {/* Tools Selector Sidebar */}
      <div className="glass-panel" style={{ padding: '1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase', padding: '0.5rem' }}>Purification Tools</h4>

        <button
          className={`btn ${activeTool === 'missing' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => { setActiveTool('missing'); clearColumnSelection(); }}
          style={{ justifyContent: 'flex-start' }}
        >
          <Trash2 size={18} /> Missing Values
        </button>

        <button
          className={`btn ${activeTool === 'duplicates' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => { setActiveTool('duplicates'); clearColumnSelection(); }}
          style={{ justifyContent: 'flex-start' }}
        >
          <CopyX size={18} /> Remove Duplicates
        </button>

        <button
          className={`btn ${activeTool === 'outliers' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => { setActiveTool('outliers'); clearColumnSelection(); }}
          style={{ justifyContent: 'flex-start' }}
        >
          <Activity size={18} /> Outlier Filtering
        </button>

        <button
          className={`btn ${activeTool === 'strings' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => { setActiveTool('strings'); clearColumnSelection(); }}
          style={{ justifyContent: 'flex-start' }}
        >
          <Type size={18} /> String Sanitation
        </button>
      </div>

      {/* Main Tool Configuration Panel */}
      <div className="glass-panel" style={{ padding: '2rem' }}>
        {/* Header */}
        <div style={{ marginBottom: '1.5rem', borderBottom: '1px solid rgba(255, 255, 255, 0.08)', paddingBottom: '1rem' }}>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#f8fafc' }}>
            {activeTool === 'missing' && 'Handle Missing Values'}
            {activeTool === 'duplicates' && 'Remove Duplicate Rows'}
            {activeTool === 'outliers' && 'Outlier Detection & Capping'}
            {activeTool === 'strings' && 'String Cleaning & Whitespace Sanitation'}
          </h3>
        </div>

        {/* Column Multi-Selector */}
        <div style={{ marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
            <label style={{ fontSize: '0.85rem', fontWeight: 600, color: '#cbd5e1' }}>
              Target Columns ({selectedCols.length} selected)
            </label>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button className="btn btn-secondary btn-sm" onClick={selectAllColumns}>Select All</button>
              <button className="btn btn-secondary btn-sm" onClick={clearColumnSelection}>Clear</button>
            </div>
          </div>

          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', maxHeight: '140px', overflowY: 'auto', background: 'rgba(15, 23, 42, 0.4)', padding: '0.75rem', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.06)' }}>
            {columnNames.map((col) => {
              const isSelected = selectedCols.includes(col);
              return (
                <button
                  key={col}
                  onClick={() => toggleColumnSelection(col)}
                  style={{
                    padding: '0.3rem 0.65rem', borderRadius: '6px', fontSize: '0.8rem', fontWeight: 500,
                    background: isSelected ? 'rgba(99, 102, 241, 0.25)' : 'rgba(255, 255, 255, 0.04)',
                    color: isSelected ? '#6366f1' : '#94a3b8',
                    border: `1px solid ${isSelected ? '#6366f1' : 'transparent'}`,
                    cursor: 'pointer', transition: 'all 0.15s ease'
                  }}
                >
                  {col}
                </button>
              );
            })}
          </div>
        </div>

        {/* Tool Specific Controls */}
        {activeTool === 'missing' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#cbd5e1', marginBottom: '0.4rem' }}>
                Strategy
              </label>
              <select className="select-field" value={missingStrategy} onChange={(e) => setMissingStrategy(e.target.value)}>
                <option value="drop_rows">Drop Rows containing missing values</option>
                <option value="drop_columns">Drop Entire Column(s)</option>
                <option value="fill_mean">Fill missing values with Mean (Numeric)</option>
                <option value="fill_median">Fill missing values with Median (Numeric)</option>
                <option value="fill_mode">Fill missing values with Mode (Categorical/Numeric)</option>
                <option value="fill_constant">Fill with Custom Value</option>
                <option value="fill_forward">Forward Fill (ffill)</option>
                <option value="fill_backward">Backward Fill (bfill)</option>
                <option value="interpolate">Linear Interpolation</option>
              </select>
            </div>

            {missingStrategy === 'fill_constant' && (
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#cbd5e1', marginBottom: '0.4rem' }}>
                  Custom Fill Value
                </label>
                <input type="text" className="input-field" value={fillValue} onChange={(e) => setFillValue(e.target.value)} placeholder="e.g. Unknown or 0" />
              </div>
            )}

            <button className="btn btn-primary" onClick={handleApplyMissing} disabled={loading} style={{ marginTop: '1rem' }}>
              <Sparkles size={16} /> {loading ? 'Purifying...' : 'Apply Missing Value Purification'}
            </button>
          </div>
        )}

        {activeTool === 'duplicates' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#cbd5e1', marginBottom: '0.4rem' }}>
                Keep Duplicate Occurrence
              </label>
              <select className="select-field" value={keepStrategy} onChange={(e) => setKeepStrategy(e.target.value)}>
                <option value="first">Keep First Occurrence (Drop remaining duplicates)</option>
                <option value="last">Keep Last Occurrence</option>
                <option value="none">Drop ALL occurrences of duplicates</option>
              </select>
            </div>

            <button className="btn btn-primary" onClick={handleApplyDuplicates} disabled={loading} style={{ marginTop: '1rem' }}>
              <Sparkles size={16} /> {loading ? 'Deduplicating...' : 'Remove Duplicate Rows'}
            </button>
          </div>
        )}

        {activeTool === 'outliers' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#cbd5e1', marginBottom: '0.4rem' }}>
                  Detection Method
                </label>
                <select className="select-field" value={outlierMethod} onChange={(e) => setOutlierMethod(e.target.value)}>
                  <option value="iqr">Interquartile Range (IQR)</option>
                  <option value="zscore">Z-Score Method</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#cbd5e1', marginBottom: '0.4rem' }}>
                  Action
                </label>
                <select className="select-field" value={outlierAction} onChange={(e) => setOutlierAction(e.target.value)}>
                  <option value="remove">Remove Outlier Rows</option>
                  <option value="cap">Cap/Winsorize Outliers (Clamp to bounds)</option>
                  <option value="replace_nan">Replace with NaN</option>
                </select>
              </div>
            </div>

            <button className="btn btn-primary" onClick={handleApplyOutliers} disabled={loading} style={{ marginTop: '1rem' }}>
              <Sparkles size={16} /> {loading ? 'Filtering Outliers...' : 'Apply Outlier Filtering'}
            </button>
          </div>
        )}

        {activeTool === 'strings' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#cbd5e1', marginBottom: '0.4rem' }}>
                Sanitation Actions
              </label>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                {['trim', 'lowercase', 'uppercase', 'titlecase', 'remove_special'].map((act) => (
                  <button
                    key={act}
                    className={`btn ${stringActions.includes(act) ? 'btn-primary' : 'btn-secondary'} btn-sm`}
                    onClick={() => setStringActions(stringActions.includes(act) ? stringActions.filter(a => a !== act) : [...stringActions, act])}
                  >
                    {act}
                  </button>
                ))}
              </div>
            </div>

            <button className="btn btn-primary" onClick={handleApplyStrings} disabled={loading} style={{ marginTop: '1rem' }}>
              <Sparkles size={16} /> {loading ? 'Sanitizing...' : 'Apply String Sanitation'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
