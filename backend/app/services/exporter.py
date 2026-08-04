"""
Exporter Service — Exports DataFrame to CSV, Excel, or HTML audit report.
"""

from io import BytesIO, StringIO
from typing import Any, Optional
import pandas as pd


def export_to_csv(df: pd.DataFrame, include_columns: Optional[list[str]] = None) -> bytes:
    """Export DataFrame to CSV bytes."""
    export_df = df[include_columns] if include_columns else df
    return export_df.to_csv(index=False).encode("utf-8")


def export_to_excel(df: pd.DataFrame, include_columns: Optional[list[str]] = None) -> bytes:
    """Export DataFrame to Excel bytes (.xlsx)."""
    export_df = df[include_columns] if include_columns else df
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        export_df.to_excel(writer, index=False, sheet_name="Cleaned Data")
    return output.getvalue()


def export_to_html_report(
    session_id: str,
    df: pd.DataFrame,
    filename: str,
    history: list[dict[str, Any]],
    scan_info: dict[str, Any],
) -> str:
    """Generate an HTML audit report summarizing data purification."""
    history_html = "".join([
        f"<tr><td>{h['index']}</td><td>{h['operation']}</td><td>{h['description']}</td>"
        f"<td>{h['rows_affected']}</td><td>{h['timestamp']}</td></tr>"
        for h in history
    ])

    sample_table = df.head(10).to_html(classes="table", index=False)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DataPurification Audit Report — {filename}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 2rem; }}
        .card {{ background: #1e293b; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; border: 1px solid #334155; }}
        h1, h2, h3 {{ color: #38bdf8; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; font-size: 0.9rem; }}
        th, td {{ padding: 0.75rem; text-align: left; border-bottom: 1px solid #334155; }}
        th {{ background-color: #0f172a; color: #94a3b8; }}
        .badge {{ background-color: #0284c7; color: white; padding: 0.25rem 0.5rem; border-radius: 4px; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>DataPurification Audit Report</h1>
    <div class="card">
        <h2>File Overview</h2>
        <p><strong>File Name:</strong> {filename}</p>
        <p><strong>Cleaned Rows:</strong> {df.shape[0]} | <strong>Cleaned Columns:</strong> {df.shape[1]}</p>
        <p><strong>Quality Score:</strong> <span class="badge">{scan_info.get('quality_score', 'N/A')}/100</span></p>
    </div>

    <div class="card">
        <h2>Purification Audit Log (Operations Performed)</h2>
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Operation</th>
                    <th>Description</th>
                    <th>Rows Affected</th>
                    <th>Timestamp</th>
                </tr>
            </thead>
            <tbody>
                {history_html}
            </tbody>
        </table>
    </div>

    <div class="card">
        <h2>Data Preview (First 10 Rows)</h2>
        {sample_table}
    </div>
</body>
</html>"""
    return html
