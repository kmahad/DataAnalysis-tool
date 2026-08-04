import React, { createContext, useContext, useState } from 'react';
import { api } from '../api/client';
import { ActiveTab, HistoryResponse, ScanReport, UploadResponse } from '../types';

interface DataContextType {
  activeSession: UploadResponse | null;
  scanReport: ScanReport | null;
  history: HistoryResponse | null;
  activeTab: ActiveTab;
  loading: boolean;
  error: string | null;
  setActiveTab: (tab: ActiveTab) => void;
  setSession: (session: UploadResponse) => void;
  refreshScanReport: () => Promise<void>;
  refreshHistory: () => Promise<void>;
  undo: () => Promise<void>;
  redo: () => Promise<void>;
  jumpHistory: (index: number) => Promise<void>;
  setError: (err: string | null) => void;
}

const DataContext = createContext<DataContextType | undefined>(undefined);

export const DataProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [activeSession, setActiveSession] = useState<UploadResponse | null>(null);
  const [scanReport, setScanReport] = useState<ScanReport | null>(null);
  const [history, setHistory] = useState<HistoryResponse | null>(null);
  const [activeTab, setActiveTab] = useState<ActiveTab>('upload');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const setSession = (session: UploadResponse) => {
    setActiveSession(session);
    setActiveTab('scan');
    fetchScan(session.session_id);
    fetchHist(session.session_id);
  };

  const fetchScan = async (sessionId: string) => {
    try {
      setLoading(true);
      const report = await api.getScanReport(sessionId);
      setScanReport(report);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchHist = async (sessionId: string) => {
    try {
      const hist = await api.getHistory(sessionId);
      setHistory(hist);
    } catch (e: any) {
      setError(e.message);
    }
  };

  const refreshScanReport = async () => {
    if (activeSession) await fetchScan(activeSession.session_id);
  };

  const refreshHistory = async () => {
    if (activeSession) await fetchHist(activeSession.session_id);
  };

  const undo = async () => {
    if (!activeSession) return;
    try {
      setLoading(true);
      const res = await api.undo(activeSession.session_id);
      setHistory(res);
      await refreshScanReport();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const redo = async () => {
    if (!activeSession) return;
    try {
      setLoading(true);
      const res = await api.redo(activeSession.session_id);
      setHistory(res);
      await refreshScanReport();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const jumpHistory = async (index: number) => {
    if (!activeSession) return;
    try {
      setLoading(true);
      const res = await api.jumpHistory(activeSession.session_id, index);
      setHistory(res);
      await refreshScanReport();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <DataContext.Provider
      value={{
        activeSession,
        scanReport,
        history,
        activeTab,
        loading,
        error,
        setActiveTab,
        setSession,
        refreshScanReport,
        refreshHistory,
        undo,
        redo,
        jumpHistory,
        setError,
      }}
    >
      {children}
    </DataContext.Provider>
  );
};

export const useData = () => {
  const ctx = useContext(DataContext);
  if (!ctx) throw new Error('useData must be used within a DataProvider');
  return ctx;
};
