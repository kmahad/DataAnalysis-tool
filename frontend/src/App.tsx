import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { DataProvider, useData } from './context/DataContext';
import { AuthModal } from './components/Auth/AuthModal';
import { Sidebar } from './components/Layout/Sidebar';
import { Header } from './components/Layout/Header';
import { FileUpload } from './components/Upload/FileUpload';
import { DatabaseConnect } from './components/Upload/DatabaseConnect';
import { ScanReport } from './components/Scanner/ScanReport';
import { DataTable } from './components/DataGrid/DataTable';
import { CleaningPanel } from './components/Cleaning/CleaningPanel';
import { ChartBuilder } from './components/Visualization/ChartBuilder';
import { HistoryPanel } from './components/History/HistoryPanel';
import { ExportPanel } from './components/Export/ExportPanel';
import { Upload, Database } from 'lucide-react';

const MainLayout: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const { activeTab } = useData();
  const [sourceTab, setSourceTab] = useState<'file' | 'db'>('file');

  if (!isAuthenticated) {
    return <AuthModal />;
  }

  return (
    <div style={{ display: 'flex', width: '100vw', height: '100vh', overflow: 'hidden' }}>
      <Sidebar />

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
        <Header />

        <main style={{ flex: 1, padding: '2rem', overflowY: 'auto' }}>
          {activeTab === 'upload' && (
            <div style={{ maxWidth: '900px', margin: '0 auto' }}>
              <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
                <button
                  className={`btn ${sourceTab === 'file' ? 'btn-primary' : 'btn-secondary'}`}
                  onClick={() => setSourceTab('file')}
                >
                  <Upload size={18} /> Upload CSV / Excel File
                </button>
                <button
                  className={`btn ${sourceTab === 'db' ? 'btn-primary' : 'btn-secondary'}`}
                  onClick={() => setSourceTab('db')}
                >
                  <Database size={18} /> Connect Cloud Database
                </button>
              </div>

              {sourceTab === 'file' ? <FileUpload /> : <DatabaseConnect />}
            </div>
          )}

          {activeTab === 'scan' && <ScanReport />}
          {activeTab === 'grid' && <DataTable />}
          {activeTab === 'clean' && <CleaningPanel />}
          {activeTab === 'visualize' && <ChartBuilder />}
          {activeTab === 'history' && <HistoryPanel />}
          {activeTab === 'export' && <ExportPanel />}
        </main>
      </div>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <DataProvider>
        <MainLayout />
      </DataProvider>
    </AuthProvider>
  );
};

export default App;
