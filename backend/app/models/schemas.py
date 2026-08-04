from pydantic import BaseModel, Field
from typing import Optional, Any
from enum import Enum
from datetime import datetime


# ─── Auth ───────────────────────────────────────────────
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ─── Data Upload ────────────────────────────────────────
class UploadResponse(BaseModel):
    session_id: str
    filename: str
    rows: int
    columns: int
    column_names: list[str]
    column_types: dict[str, str]
    preview: list[dict[str, Any]]


# ─── Database Connection ────────────────────────────────
class DatabaseType(str, Enum):
    sqlite = "sqlite"
    postgresql = "postgresql"
    mysql = "mysql"


class DatabaseConnectRequest(BaseModel):
    db_type: DatabaseType
    connection_string: str
    query: Optional[str] = None
    table_name: Optional[str] = None


class DatabaseTablesResponse(BaseModel):
    tables: list[str]


# ─── Scanner ────────────────────────────────────────────
class ColumnProfile(BaseModel):
    name: str
    dtype: str
    non_null_count: int
    null_count: int
    null_percentage: float
    unique_count: int
    unique_percentage: float
    sample_values: list[Any]
    # Numeric-only fields
    mean: Optional[float] = None
    median: Optional[float] = None
    std: Optional[float] = None
    min_val: Optional[Any] = None
    max_val: Optional[Any] = None
    q1: Optional[float] = None
    q3: Optional[float] = None
    outlier_count: Optional[int] = None
    # String-only fields
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    avg_length: Optional[float] = None


class ScanReport(BaseModel):
    session_id: str
    total_rows: int
    total_columns: int
    total_cells: int
    missing_cells: int
    missing_percentage: float
    duplicate_rows: int
    duplicate_percentage: float
    quality_score: float  # 0-100
    columns: list[ColumnProfile]
    recommendations: list[dict[str, Any]]
    missing_matrix: Optional[list[list[int]]] = None  # rows x cols binary matrix (sampled)


# ─── Cleaning Operations ────────────────────────────────
class CleaningOperation(str, Enum):
    handle_missing = "handle_missing"
    remove_duplicates = "remove_duplicates"
    handle_outliers = "handle_outliers"
    convert_types = "convert_types"
    clean_strings = "clean_strings"
    column_operations = "column_operations"


class MissingValueStrategy(str, Enum):
    drop_rows = "drop_rows"
    drop_columns = "drop_columns"
    fill_mean = "fill_mean"
    fill_median = "fill_median"
    fill_mode = "fill_mode"
    fill_constant = "fill_constant"
    fill_forward = "fill_forward"
    fill_backward = "fill_backward"
    interpolate = "interpolate"


class HandleMissingRequest(BaseModel):
    session_id: str
    columns: list[str]
    strategy: MissingValueStrategy
    fill_value: Optional[Any] = None  # Used with fill_constant
    threshold: Optional[float] = None  # For drop_columns: drop if > threshold% missing


class DuplicateKeep(str, Enum):
    first = "first"
    last = "last"
    none = "none"  # drop all duplicates


class RemoveDuplicatesRequest(BaseModel):
    session_id: str
    subset_columns: Optional[list[str]] = None  # None = all columns
    keep: DuplicateKeep = DuplicateKeep.first


class OutlierMethod(str, Enum):
    iqr = "iqr"
    zscore = "zscore"


class OutlierAction(str, Enum):
    remove = "remove"
    cap = "cap"
    replace_nan = "replace_nan"


class HandleOutliersRequest(BaseModel):
    session_id: str
    columns: list[str]
    method: OutlierMethod = OutlierMethod.iqr
    action: OutlierAction = OutlierAction.remove
    threshold: float = 1.5  # IQR multiplier or Z-score threshold


class ConvertTypesRequest(BaseModel):
    session_id: str
    conversions: dict[str, str]  # column_name -> target_type (int, float, str, datetime, category)
    datetime_format: Optional[str] = None


class StringCleanAction(str, Enum):
    trim = "trim"
    lowercase = "lowercase"
    uppercase = "uppercase"
    titlecase = "titlecase"
    remove_special = "remove_special"
    regex_replace = "regex_replace"


class CleanStringsRequest(BaseModel):
    session_id: str
    columns: list[str]
    actions: list[StringCleanAction]
    regex_pattern: Optional[str] = None
    regex_replacement: Optional[str] = None


class ColumnAction(str, Enum):
    rename = "rename"
    drop = "drop"
    reorder = "reorder"


class ColumnOperationsRequest(BaseModel):
    session_id: str
    action: ColumnAction
    rename_map: Optional[dict[str, str]] = None  # old_name -> new_name
    drop_columns: Optional[list[str]] = None
    new_order: Optional[list[str]] = None


# ─── Cleaning Response ──────────────────────────────────
class CleaningResult(BaseModel):
    session_id: str
    operation: str
    description: str
    rows_before: int
    rows_after: int
    columns_before: int
    columns_after: int
    rows_affected: int
    columns_affected: list[str]
    timestamp: str
    history_index: int
    preview: list[dict[str, Any]]


# ─── History / Undo-Redo ────────────────────────────────
class HistoryEntry(BaseModel):
    index: int
    operation: str
    description: str
    rows_affected: int
    columns_affected: list[str]
    timestamp: str
    is_current: bool


class HistoryResponse(BaseModel):
    session_id: str
    entries: list[HistoryEntry]
    current_index: int
    can_undo: bool
    can_redo: bool


# ─── Visualization ──────────────────────────────────────
class ChartType(str, Enum):
    bar = "bar"
    line = "line"
    scatter = "scatter"
    pie = "pie"
    histogram = "histogram"
    box = "box"
    violin = "violin"
    heatmap = "heatmap"


class ChartRequest(BaseModel):
    session_id: str
    chart_type: ChartType
    x_column: Optional[str] = None
    y_column: Optional[str] = None
    color_column: Optional[str] = None
    title: Optional[str] = None
    aggregation: Optional[str] = None  # sum, mean, count, etc.


class ChartResponse(BaseModel):
    chart_json: dict[str, Any]  # Plotly figure JSON


# ─── Export ─────────────────────────────────────────────
class ExportFormat(str, Enum):
    csv = "csv"
    excel = "excel"
    html_report = "html_report"
    powerpoint = "powerpoint"


class ExportRequest(BaseModel):
    session_id: str
    format: ExportFormat
    include_columns: Optional[list[str]] = None
    include_charts: Optional[bool] = True


# ─── Generic ────────────────────────────────────────────
class DataPreviewResponse(BaseModel):
    session_id: str
    rows: int
    columns: int
    column_names: list[str]
    column_types: dict[str, str]
    data: list[dict[str, Any]]
    total_rows: int


class MessageResponse(BaseModel):
    message: str
    detail: Optional[str] = None
