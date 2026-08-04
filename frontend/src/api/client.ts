import { CleaningResult, HistoryResponse, ScanReport, UploadResponse } from '../types';

const API_BASE = '/api';

function getAuthHeader(): Record<string, string> {
  const token = localStorage.getItem('datapurify_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const headers = {
    ...getAuthHeader(),
    ...(options.headers || {}),
  };

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(err.detail || 'API request failed');
  }

  return response.json();
}

export const api = {
  // Auth
  login: (credentials: any) =>
    request<{ access_token: string }>('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials),
    }),

  register: (credentials: any) =>
    request<{ access_token: string }>('/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials),
    }),

  getMe: () => request<{ username: string }>('/auth/me'),

  // Upload
  uploadFile: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return request<UploadResponse>('/upload', {
      method: 'POST',
      body: formData,
    });
  },

  // Database
  connectDatabase: (data: any) =>
    request<UploadResponse>('/database/load', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }),

  getDatabaseTables: (data: any) =>
    request<{ tables: string[] }>('/database/tables', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }),

  // Scan
  getScanReport: (sessionId: string) => request<ScanReport>(`/scan/${sessionId}`),

  getPreview: (sessionId: string, page = 1, pageSize = 50) =>
    request<any>(`/scan/${sessionId}/preview?page=${page}&page_size=${pageSize}`),

  // Cleaning operations
  cleanMissing: (data: any) =>
    request<CleaningResult>('/clean/missing', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }),

  cleanDuplicates: (data: any) =>
    request<CleaningResult>('/clean/duplicates', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }),

  cleanOutliers: (data: any) =>
    request<CleaningResult>('/clean/outliers', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }),

  cleanTypes: (data: any) =>
    request<CleaningResult>('/clean/types', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }),

  cleanStrings: (data: any) =>
    request<CleaningResult>('/clean/strings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }),

  cleanColumns: (data: any) =>
    request<CleaningResult>('/clean/columns', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }),

  // History & Undo / Redo
  getHistory: (sessionId: string) => request<HistoryResponse>(`/clean/history/${sessionId}`),

  undo: (sessionId: string) =>
    request<HistoryResponse>(`/clean/undo/${sessionId}`, { method: 'POST' }),

  redo: (sessionId: string) =>
    request<HistoryResponse>(`/clean/redo/${sessionId}`, { method: 'POST' }),

  jumpHistory: (sessionId: string, index: number) =>
    request<HistoryResponse>(`/clean/jump/${sessionId}/${index}`, { method: 'POST' }),

  // Visualization
  generateChart: (data: any) =>
    request<{ chart_json: any }>('/visualize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }),

  // Export
  exportData: async (data: any) => {
    const response = await fetch('/api/export', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader(),
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Export failed');
    return response;
  },
};
