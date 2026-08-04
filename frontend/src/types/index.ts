export interface User {
  username: string;
}

export interface UploadResponse {
  session_id: string;
  filename: string;
  rows: number;
  columns: number;
  column_names: string[];
  column_types: Record<string, string>;
  preview: Record<string, any>[];
}

export interface ColumnProfile {
  name: string;
  dtype: string;
  non_null_count: number;
  null_count: number;
  null_percentage: number;
  unique_count: number;
  unique_percentage: number;
  sample_values: any[];
  mean?: number;
  median?: number;
  std?: number;
  min_val?: any;
  max_val?: any;
  q1?: number;
  q3?: number;
  outlier_count?: number;
  min_length?: number;
  max_length?: number;
  avg_length?: number;
}

export interface Recommendation {
  type: string;
  severity: 'low' | 'medium' | 'high';
  column: string;
  message: string;
  suggested_action: string;
}

export interface ScanReport {
  session_id: string;
  total_rows: number;
  total_columns: number;
  total_cells: number;
  missing_cells: number;
  missing_percentage: number;
  duplicate_rows: number;
  duplicate_percentage: number;
  quality_score: number;
  columns: ColumnProfile[];
  recommendations: Recommendation[];
  missing_matrix?: number[][];
}

export interface HistoryEntry {
  index: number;
  operation: string;
  description: string;
  rows_affected: number;
  columns_affected: string[];
  timestamp: string;
  is_current: boolean;
}

export interface HistoryResponse {
  session_id: string;
  entries: HistoryEntry[];
  current_index: number;
  can_undo: boolean;
  can_redo: boolean;
}

export interface CleaningResult {
  session_id: string;
  operation: string;
  description: string;
  rows_before: number;
  rows_after: number;
  columns_before: number;
  columns_after: number;
  rows_affected: number;
  columns_affected: string[];
  timestamp: string;
  history_index: number;
  preview: Record<string, any>[];
}

export type ActiveTab = 'upload' | 'scan' | 'grid' | 'clean' | 'visualize' | 'history' | 'export';
