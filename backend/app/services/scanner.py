"""
Data Scanner Service — Profiles a DataFrame and produces a comprehensive quality report.
"""

from typing import Any
import numpy as np
import pandas as pd


def profile_column(series: pd.Series) -> dict[str, Any]:
    """Profile a single column."""
    total = len(series)
    null_count = int(series.isna().sum())
    non_null = total - null_count
    unique_count = int(series.nunique())

    profile: dict[str, Any] = {
        "name": series.name,
        "dtype": str(series.dtype),
        "non_null_count": non_null,
        "null_count": null_count,
        "null_percentage": round(null_count / total * 100, 2) if total > 0 else 0,
        "unique_count": unique_count,
        "unique_percentage": round(unique_count / non_null * 100, 2) if non_null > 0 else 0,
        "sample_values": series.dropna().head(5).tolist(),
    }

    # Numeric-specific profiling
    if pd.api.types.is_numeric_dtype(series):
        clean = series.dropna()
        if len(clean) > 0:
            q1 = float(clean.quantile(0.25))
            q3 = float(clean.quantile(0.75))
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            outliers = ((clean < lower) | (clean > upper)).sum()

            profile.update({
                "mean": round(float(clean.mean()), 4),
                "median": round(float(clean.median()), 4),
                "std": round(float(clean.std()), 4),
                "min_val": float(clean.min()),
                "max_val": float(clean.max()),
                "q1": round(q1, 4),
                "q3": round(q3, 4),
                "outlier_count": int(outliers),
            })

    # String-specific profiling
    elif pd.api.types.is_string_dtype(series) or pd.api.types.is_object_dtype(series):
        str_series = series.dropna().astype(str)
        if len(str_series) > 0:
            lengths = str_series.str.len()
            profile.update({
                "min_length": int(lengths.min()),
                "max_length": int(lengths.max()),
                "avg_length": round(float(lengths.mean()), 2),
            })

    return profile


def generate_recommendations(df: pd.DataFrame, column_profiles: list[dict]) -> list[dict[str, Any]]:
    """Generate cleaning recommendations based on the scan."""
    recs = []

    for col_profile in column_profiles:
        col_name = col_profile["name"]

        # High missing values
        if col_profile["null_percentage"] > 50:
            recs.append({
                "type": "handle_missing",
                "severity": "high",
                "column": col_name,
                "message": f"Column '{col_name}' has {col_profile['null_percentage']:.1f}% missing values. Consider dropping this column.",
                "suggested_action": "drop_columns",
            })
        elif col_profile["null_percentage"] > 5:
            fill_strategy = "fill_mean" if col_profile.get("mean") is not None else "fill_mode"
            recs.append({
                "type": "handle_missing",
                "severity": "medium",
                "column": col_name,
                "message": f"Column '{col_name}' has {col_profile['null_percentage']:.1f}% missing values.",
                "suggested_action": fill_strategy,
            })

        # Outliers
        if col_profile.get("outlier_count") and col_profile["outlier_count"] > 0:
            pct = col_profile["outlier_count"] / col_profile["non_null_count"] * 100
            if pct > 5:
                recs.append({
                    "type": "handle_outliers",
                    "severity": "medium",
                    "column": col_name,
                    "message": f"Column '{col_name}' has {col_profile['outlier_count']} outliers ({pct:.1f}%).",
                    "suggested_action": "cap",
                })

        # Low cardinality → suggest category
        if col_profile["dtype"] == "object" and col_profile["unique_count"] < 20 and col_profile["non_null_count"] > 100:
            recs.append({
                "type": "convert_types",
                "severity": "low",
                "column": col_name,
                "message": f"Column '{col_name}' has only {col_profile['unique_count']} unique values. Consider converting to category type for efficiency.",
                "suggested_action": "category",
            })

    # Duplicate rows
    dup_count = int(df.duplicated().sum())
    if dup_count > 0:
        recs.append({
            "type": "remove_duplicates",
            "severity": "medium",
            "column": "__all__",
            "message": f"Dataset has {dup_count} duplicate rows ({dup_count / len(df) * 100:.1f}%).",
            "suggested_action": "first",
        })

    return recs


def compute_quality_score(df: pd.DataFrame, column_profiles: list[dict]) -> float:
    """Compute a 0-100 data quality score."""
    total_cells = df.shape[0] * df.shape[1]
    if total_cells == 0:
        return 0.0

    # Completeness (40% weight): percentage of non-null cells
    missing = sum(cp["null_count"] for cp in column_profiles)
    completeness = (1 - missing / total_cells) * 100

    # Uniqueness (20% weight): 100 - duplicate row percentage
    dup_pct = df.duplicated().sum() / len(df) * 100 if len(df) > 0 else 0
    uniqueness = 100 - dup_pct

    # Consistency (20% weight): low outlier percentage
    total_outliers = sum(cp.get("outlier_count", 0) or 0 for cp in column_profiles)
    numeric_cells = sum(cp["non_null_count"] for cp in column_profiles if cp.get("mean") is not None)
    consistency = (1 - total_outliers / numeric_cells) * 100 if numeric_cells > 0 else 100

    # Validity (20% weight): reasonable type inference
    validity = 100  # Start at 100, penalize for mixed types
    for cp in column_profiles:
        if cp["dtype"] == "object" and cp.get("mean") is None:
            # Check if it looks like it should be numeric
            pass  # Simplified for MVP

    score = (completeness * 0.4) + (uniqueness * 0.2) + (consistency * 0.2) + (validity * 0.2)
    return round(max(0, min(100, score)), 1)


def generate_missing_matrix(df: pd.DataFrame, max_rows: int = 200) -> list[list[int]]:
    """Generate a binary missing values matrix (1 = missing, 0 = present).
    Samples rows if dataset is large.
    """
    if len(df) > max_rows:
        sample_df = df.sample(n=max_rows, random_state=42).sort_index()
    else:
        sample_df = df

    return sample_df.isna().astype(int).values.tolist()


def scan_dataframe(df: pd.DataFrame, session_id: str) -> dict[str, Any]:
    """Run the full scan and return a report dict."""
    column_profiles = [profile_column(df[col]) for col in df.columns]
    recommendations = generate_recommendations(df, column_profiles)
    quality_score = compute_quality_score(df, column_profiles)
    missing_matrix = generate_missing_matrix(df)

    total_cells = df.shape[0] * df.shape[1]
    missing_cells = int(df.isna().sum().sum())
    dup_rows = int(df.duplicated().sum())

    return {
        "session_id": session_id,
        "total_rows": df.shape[0],
        "total_columns": df.shape[1],
        "total_cells": total_cells,
        "missing_cells": missing_cells,
        "missing_percentage": round(missing_cells / total_cells * 100, 2) if total_cells > 0 else 0,
        "duplicate_rows": dup_rows,
        "duplicate_percentage": round(dup_rows / len(df) * 100, 2) if len(df) > 0 else 0,
        "quality_score": quality_score,
        "columns": column_profiles,
        "recommendations": recommendations,
        "missing_matrix": missing_matrix,
    }
