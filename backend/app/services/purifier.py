"""
Data Purifier Service — Performs cleaning operations on DataFrames.
Each function takes a DataFrame and returns a new (cleaned) DataFrame + metadata.
"""

import re
from typing import Any, Optional

import numpy as np
import pandas as pd


def handle_missing_values(
    df: pd.DataFrame,
    columns: list[str],
    strategy: str,
    fill_value: Any = None,
    threshold: Optional[float] = None,
) -> tuple[pd.DataFrame, str, int]:
    """Handle missing values. Returns (new_df, description, rows_affected)."""
    result = df.copy()
    original_rows = len(result)

    if strategy == "drop_rows":
        result = result.dropna(subset=columns)
        affected = original_rows - len(result)
        desc = f"Dropped {affected} rows with missing values in columns: {', '.join(columns)}"

    elif strategy == "drop_columns":
        if threshold is not None:
            # Drop columns where missing % exceeds threshold
            cols_to_drop = [c for c in columns if result[c].isna().mean() * 100 > threshold]
        else:
            cols_to_drop = columns
        result = result.drop(columns=cols_to_drop)
        affected = len(cols_to_drop)
        desc = f"Dropped columns: {', '.join(cols_to_drop)}"

    elif strategy == "fill_mean":
        for col in columns:
            if pd.api.types.is_numeric_dtype(result[col]):
                result[col] = result[col].fillna(result[col].mean())
        affected = int(df[columns].isna().sum().sum())
        desc = f"Filled missing values with mean in: {', '.join(columns)}"

    elif strategy == "fill_median":
        for col in columns:
            if pd.api.types.is_numeric_dtype(result[col]):
                result[col] = result[col].fillna(result[col].median())
        affected = int(df[columns].isna().sum().sum())
        desc = f"Filled missing values with median in: {', '.join(columns)}"

    elif strategy == "fill_mode":
        for col in columns:
            mode_val = result[col].mode()
            if len(mode_val) > 0:
                result[col] = result[col].fillna(mode_val.iloc[0])
        affected = int(df[columns].isna().sum().sum())
        desc = f"Filled missing values with mode in: {', '.join(columns)}"

    elif strategy == "fill_constant":
        for col in columns:
            result[col] = result[col].fillna(fill_value)
        affected = int(df[columns].isna().sum().sum())
        desc = f"Filled missing values with '{fill_value}' in: {', '.join(columns)}"

    elif strategy == "fill_forward":
        for col in columns:
            result[col] = result[col].ffill()
        affected = int(df[columns].isna().sum().sum())
        desc = f"Forward-filled missing values in: {', '.join(columns)}"

    elif strategy == "fill_backward":
        for col in columns:
            result[col] = result[col].bfill()
        affected = int(df[columns].isna().sum().sum())
        desc = f"Backward-filled missing values in: {', '.join(columns)}"

    elif strategy == "interpolate":
        for col in columns:
            if pd.api.types.is_numeric_dtype(result[col]):
                result[col] = result[col].interpolate()
        affected = int(df[columns].isna().sum().sum())
        desc = f"Interpolated missing values in: {', '.join(columns)}"

    else:
        raise ValueError(f"Unknown strategy: {strategy}")

    return result, desc, affected


def remove_duplicates(
    df: pd.DataFrame,
    subset_columns: Optional[list[str]] = None,
    keep: str = "first",
) -> tuple[pd.DataFrame, str, int]:
    """Remove duplicate rows. Returns (new_df, description, rows_affected)."""
    keep_val = keep if keep != "none" else False
    result = df.drop_duplicates(subset=subset_columns, keep=keep_val)
    affected = len(df) - len(result)
    cols = ", ".join(subset_columns) if subset_columns else "all columns"
    desc = f"Removed {affected} duplicate rows (based on {cols}, keep={keep})"
    return result, desc, affected


def handle_outliers(
    df: pd.DataFrame,
    columns: list[str],
    method: str = "iqr",
    action: str = "remove",
    threshold: float = 1.5,
) -> tuple[pd.DataFrame, str, int]:
    """Handle outliers. Returns (new_df, description, rows_affected)."""
    result = df.copy()
    total_affected = 0

    for col in columns:
        if not pd.api.types.is_numeric_dtype(result[col]):
            continue

        series = result[col].dropna()

        if method == "iqr":
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - threshold * iqr
            upper = q3 + threshold * iqr
            mask = (result[col] < lower) | (result[col] > upper)
        elif method == "zscore":
            mean = series.mean()
            std = series.std()
            if std == 0:
                continue
            z_scores = (result[col] - mean) / std
            mask = z_scores.abs() > threshold
        else:
            raise ValueError(f"Unknown outlier method: {method}")

        outlier_count = int(mask.sum())
        total_affected += outlier_count

        if action == "remove":
            result = result[~mask]
        elif action == "cap":
            if method == "iqr":
                result.loc[result[col] < lower, col] = lower
                result.loc[result[col] > upper, col] = upper
            else:
                mean = series.mean()
                std = series.std()
                result.loc[mask & (result[col] > mean), col] = mean + threshold * std
                result.loc[mask & (result[col] < mean), col] = mean - threshold * std
        elif action == "replace_nan":
            result.loc[mask, col] = np.nan

    method_name = "IQR" if method == "iqr" else "Z-score"
    desc = f"Handled {total_affected} outliers in {', '.join(columns)} using {method_name} ({action})"
    return result, desc, total_affected


def convert_types(
    df: pd.DataFrame,
    conversions: dict[str, str],
    datetime_format: Optional[str] = None,
) -> tuple[pd.DataFrame, str, int]:
    """Convert column data types. Returns (new_df, description, columns_affected)."""
    result = df.copy()
    converted = []

    for col, target_type in conversions.items():
        if col not in result.columns:
            continue
        try:
            if target_type == "int":
                result[col] = pd.to_numeric(result[col], errors="coerce").astype("Int64")
            elif target_type == "float":
                result[col] = pd.to_numeric(result[col], errors="coerce")
            elif target_type == "str":
                result[col] = result[col].astype(str)
            elif target_type == "datetime":
                result[col] = pd.to_datetime(result[col], format=datetime_format, errors="coerce")
            elif target_type == "category":
                result[col] = result[col].astype("category")
            converted.append(f"{col} → {target_type}")
        except Exception:
            pass  # Skip if conversion fails

    desc = f"Converted types: {'; '.join(converted)}"
    return result, desc, len(converted)


def clean_strings(
    df: pd.DataFrame,
    columns: list[str],
    actions: list[str],
    regex_pattern: Optional[str] = None,
    regex_replacement: Optional[str] = None,
) -> tuple[pd.DataFrame, str, int]:
    """Clean string columns. Returns (new_df, description, rows_affected)."""
    result = df.copy()
    total_affected = 0

    for col in columns:
        if col not in result.columns:
            continue

        original = result[col].copy()

        for action in actions:
            if action == "trim":
                result[col] = result[col].astype(str).str.strip()
            elif action == "lowercase":
                result[col] = result[col].astype(str).str.lower()
            elif action == "uppercase":
                result[col] = result[col].astype(str).str.upper()
            elif action == "titlecase":
                result[col] = result[col].astype(str).str.title()
            elif action == "remove_special":
                result[col] = result[col].astype(str).str.replace(r'[^a-zA-Z0-9\s]', '', regex=True)
            elif action == "regex_replace" and regex_pattern:
                result[col] = result[col].astype(str).str.replace(
                    regex_pattern, regex_replacement or "", regex=True
                )

        changed = (original.astype(str) != result[col].astype(str)).sum()
        total_affected += int(changed)

    action_names = ", ".join(actions)
    desc = f"Applied string cleaning ({action_names}) to columns: {', '.join(columns)}"
    return result, desc, total_affected


def column_operations(
    df: pd.DataFrame,
    action: str,
    rename_map: Optional[dict[str, str]] = None,
    drop_columns: Optional[list[str]] = None,
    new_order: Optional[list[str]] = None,
) -> tuple[pd.DataFrame, str, int]:
    """Perform column-level operations. Returns (new_df, description, columns_affected)."""
    result = df.copy()

    if action == "rename" and rename_map:
        result = result.rename(columns=rename_map)
        desc = f"Renamed columns: {'; '.join(f'{k} → {v}' for k, v in rename_map.items())}"
        return result, desc, len(rename_map)

    elif action == "drop" and drop_columns:
        existing = [c for c in drop_columns if c in result.columns]
        result = result.drop(columns=existing)
        desc = f"Dropped columns: {', '.join(existing)}"
        return result, desc, len(existing)

    elif action == "reorder" and new_order:
        # Include any columns not in new_order at the end
        remaining = [c for c in result.columns if c not in new_order]
        result = result[new_order + remaining]
        desc = f"Reordered columns"
        return result, desc, len(new_order)

    return result, "No changes", 0
