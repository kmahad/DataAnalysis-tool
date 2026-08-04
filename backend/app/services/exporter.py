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


# ─── PowerPoint Export ──────────────────────────────────────────────────────────

def _rgb(hex_str: str):
    """Convert '#RRGGBB' to an RGBColor."""
    from pptx.dml.color import RGBColor
    hex_str = hex_str.lstrip("#")
    return RGBColor(int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16))


# Brand palette
_BG_DARK = "0F172A"
_CARD_BG = "1E293B"
_ACCENT = "6366F1"
_ACCENT2 = "06B6D4"
_GREEN = "10B981"
_PURPLE = "A855F7"
_TEXT_PRIMARY = "F8FAFC"
_TEXT_SECONDARY = "94A3B8"
_BORDER = "334155"


def _set_slide_bg(slide, hex_color: str):
    """Fill a slide background with a solid color."""
    from pptx.dml.color import RGBColor
    from pptx.oxml.ns import qn
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor.from_string(hex_color)


def _add_textbox(slide, left, top, width, height, text, font_size=12,
                 bold=False, color=_TEXT_PRIMARY, alignment=None, font_name="Calibri"):
    """Helper to add a styled text box to a slide."""
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
    txBox = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.bold = bold
    p.font.color.rgb = RGBColor.from_string(color)
    p.font.name = font_name
    if alignment:
        p.alignment = alignment
    return txBox


def _add_rounded_card(slide, left, top, width, height, fill_hex=_CARD_BG):
    """Add a rounded rectangle card shape."""
    from pptx.util import Inches
    from pptx.dml.color import RGBColor
    from pptx.enum.shapes import MSO_SHAPE
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor.from_string(fill_hex)
    shape.line.fill.background()
    return shape


def _generate_chart_image(fig_dict: dict, width: int = 800, height: int = 500) -> bytes:
    """Convert a Plotly figure dict to PNG bytes via Kaleido."""
    import plotly.graph_objects as go
    import plotly.io as pio
    fig = go.Figure(fig_dict)
    return pio.to_image(fig, format="png", width=width, height=height, scale=2)


def _build_correlation_analysis(df) -> tuple:
    """Build correlation heatmap chart dict and analytical summary text.
    Returns (chart_dict | None, summary_text).
    """
    import plotly.express as px
    import json
    numeric_df = df.select_dtypes(include=["number"])
    if numeric_df.shape[1] < 2:
        return None, ""

    corr = numeric_df.corr()
    fig = px.imshow(
        corr, text_auto=".2f", aspect="auto",
        title="Correlation Heatmap",
        color_continuous_scale="Viridis",
        template="plotly_dark",
    )
    fig.update_layout(
        paper_bgcolor="rgba(15,23,42,1)",
        plot_bgcolor="rgba(15,23,42,1)",
        font=dict(color="#e2e8f0", family="Calibri"),
        margin=dict(l=20, r=20, t=40, b=20),
    )
    chart_dict = json.loads(fig.to_json())

    # Analytical summary
    lines = []
    strong_pos, strong_neg = [], []
    for i in range(len(corr.columns)):
        for j in range(i + 1, len(corr.columns)):
            val = corr.iloc[i, j]
            pair = f"{corr.columns[i]} ↔ {corr.columns[j]}"
            if val >= 0.7:
                strong_pos.append((pair, val))
            elif val <= -0.7:
                strong_neg.append((pair, val))

    if strong_pos:
        lines.append("Strong positive correlations detected:")
        for pair, v in strong_pos[:5]:
            lines.append(f"  • {pair}: r = {v:.2f}")
        lines.append("→ These columns move together. Consider checking for redundancy or multicollinearity before modeling.")
    if strong_neg:
        lines.append("Strong negative correlations detected:")
        for pair, v in strong_neg[:5]:
            lines.append(f"  • {pair}: r = {v:.2f}")
        lines.append("→ Inversely related features — may be useful as complementary predictors.")
    if not strong_pos and not strong_neg:
        lines.append("No strong correlations (|r| ≥ 0.7) found between numeric columns.")
        lines.append("→ Features appear largely independent, which is favorable for most modeling techniques.")

    return chart_dict, "\n".join(lines)


def _build_numeric_distribution(df) -> tuple:
    """Build histogram for the first key numeric column and analytical summary.
    Returns (chart_dict | None, summary_text, column_name).
    """
    import plotly.express as px
    import json
    import numpy as np
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    if not numeric_cols:
        return None, "", ""

    # Pick the column with highest variance (most interesting distribution)
    col = max(numeric_cols, key=lambda c: df[c].var() if df[c].notna().sum() > 1 else 0)
    clean = df[col].dropna()
    if len(clean) == 0:
        return None, "", col

    fig = px.histogram(
        df, x=col, title=f"Distribution of '{col}'",
        template="plotly_dark",
        color_discrete_sequence=["#6366f1"],
    )
    fig.update_layout(
        paper_bgcolor="rgba(15,23,42,1)",
        plot_bgcolor="rgba(15,23,42,1)",
        font=dict(color="#e2e8f0", family="Calibri"),
        margin=dict(l=20, r=20, t=40, b=20),
    )
    chart_dict = json.loads(fig.to_json())

    # Analysis
    lines = []
    mean_val = clean.mean()
    median_val = clean.median()
    std_val = clean.std()
    skew_val = clean.skew()
    q1 = clean.quantile(0.25)
    q3 = clean.quantile(0.75)
    iqr = q3 - q1
    outlier_count = int(((clean < q1 - 1.5 * iqr) | (clean > q3 + 1.5 * iqr)).sum())

    lines.append(f"Column: {col}  |  Mean: {mean_val:.2f}  |  Median: {median_val:.2f}  |  Std Dev: {std_val:.2f}")

    if abs(skew_val) < 0.5:
        lines.append(f"Distribution is approximately symmetric (skewness: {skew_val:.2f}).")
        lines.append("→ Suitable for parametric statistical methods without transformation.")
    elif skew_val >= 0.5:
        lines.append(f"Distribution is right-skewed (skewness: {skew_val:.2f}).")
        lines.append("→ Consider log or square-root transformation if normality is required for analysis.")
    else:
        lines.append(f"Distribution is left-skewed (skewness: {skew_val:.2f}).")
        lines.append("→ Consider exponential or power transformation to normalize.")

    if outlier_count > 0:
        lines.append(f"{outlier_count} outlier(s) detected via IQR method ({outlier_count / len(clean) * 100:.1f}% of values).")
        lines.append("→ Outliers may inflate mean and standard deviation. Consider capping or investigating root cause.")
    else:
        lines.append("No outliers detected via IQR method — data is well-contained.")

    return chart_dict, "\n".join(lines), col


def _build_categorical_distribution(df) -> tuple:
    """Build bar chart for the first key categorical column and analytical summary.
    Returns (chart_dict | None, summary_text, column_name).
    """
    import plotly.express as px
    import json
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    if not cat_cols:
        return None, "", ""

    # Pick column with lowest cardinality (most meaningful categories)
    col = min(cat_cols, key=lambda c: df[c].nunique())
    counts = df[col].value_counts()
    if len(counts) == 0:
        return None, "", col

    # Truncate to top 15 for readability
    display_counts = counts.head(15)
    chart_df_local = display_counts.reset_index()
    chart_df_local.columns = [col, "Count"]

    fig = px.bar(
        chart_df_local, x=col, y="Count",
        title=f"Category Counts for '{col}'",
        template="plotly_dark",
        color_discrete_sequence=["#06b6d4"],
    )
    fig.update_layout(
        paper_bgcolor="rgba(15,23,42,1)",
        plot_bgcolor="rgba(15,23,42,1)",
        font=dict(color="#e2e8f0", family="Calibri"),
        margin=dict(l=20, r=20, t=40, b=20),
    )
    chart_dict = json.loads(fig.to_json())

    # Analysis
    lines = []
    total = int(counts.sum())
    n_unique = len(counts)
    top_cat = counts.index[0]
    top_pct = counts.iloc[0] / total * 100

    lines.append(f"Column: {col}  |  {n_unique} unique categories  |  {total} total values")
    lines.append(f"Most frequent: '{top_cat}' ({counts.iloc[0]} occurrences, {top_pct:.1f}%)")

    if top_pct > 80:
        lines.append(f"→ Highly imbalanced: '{top_cat}' dominates with {top_pct:.1f}% of all values.")
        lines.append("  This column may have low predictive power or require resampling techniques.")
    elif top_pct > 50:
        lines.append(f"→ Moderately imbalanced: '{top_cat}' represents the majority at {top_pct:.1f}%.")
        lines.append("  Consider stratified sampling if using for classification.")
    else:
        lines.append("→ Reasonably balanced distribution across categories.")

    if n_unique > 50:
        lines.append(f"⚠ High cardinality ({n_unique} categories) — consider grouping rare categories or encoding.")

    return chart_dict, "\n".join(lines), col


def export_to_powerpoint(
    session_id: str,
    df: pd.DataFrame,
    filename: str,
    history: list[dict[str, Any]],
    scan_info: dict[str, Any],
) -> bytes:
    """Generate a premium dark-themed PowerPoint report with charts and analytical insights."""
    from pptx import Presentation
    from pptx.util import Inches, Pt, Emu
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
    from datetime import datetime

    prs = Presentation()
    # Set widescreen 16:9
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]  # Blank layout

    # ──────────────────────────────────────────────────────
    # SLIDE 1 — Title Slide
    # ──────────────────────────────────────────────────────
    slide1 = prs.slides.add_slide(blank_layout)
    _set_slide_bg(slide1, _BG_DARK)

    # Accent line
    _add_rounded_card(slide1, 1.5, 2.2, 10.3, 0.06, _ACCENT)

    _add_textbox(slide1, 1.5, 2.5, 10, 1.2, "DataPurify", font_size=44, bold=True, color=_TEXT_PRIMARY)
    _add_textbox(slide1, 1.5, 3.5, 10, 0.8, "Data Quality & Analysis Report", font_size=24, color=_ACCENT)
    _add_textbox(slide1, 1.5, 4.5, 10, 0.5, f"Dataset: {filename}", font_size=14, color=_TEXT_SECONDARY)
    _add_textbox(slide1, 1.5, 5.0, 10, 0.5,
                 f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
                 font_size=12, color=_TEXT_SECONDARY)

    # ──────────────────────────────────────────────────────
    # SLIDE 2 — Executive Summary Dashboard
    # ──────────────────────────────────────────────────────
    slide2 = prs.slides.add_slide(blank_layout)
    _set_slide_bg(slide2, _BG_DARK)
    _add_textbox(slide2, 0.6, 0.3, 12, 0.6, "Executive Summary", font_size=28, bold=True, color=_TEXT_PRIMARY)
    _add_rounded_card(slide2, 0.6, 0.85, 12, 0.04, _ACCENT)

    metrics = [
        ("Total Rows", str(scan_info.get("total_rows", "—")), _ACCENT2),
        ("Total Columns", str(scan_info.get("total_columns", "—")), _ACCENT2),
        ("Quality Score", f"{scan_info.get('quality_score', 0)}/100", _GREEN),
        ("Missing Cells", f"{scan_info.get('missing_cells', 0)} ({scan_info.get('missing_percentage', 0):.1f}%)", _PURPLE),
        ("Duplicate Rows", f"{scan_info.get('duplicate_rows', 0)} ({scan_info.get('duplicate_percentage', 0):.1f}%)", _PURPLE),
        ("Operations Done", str(max(len(history) - 1, 0)), _ACCENT),
    ]
    card_w = 3.8
    card_h = 1.6
    gap = 0.3
    start_x = 0.6
    for idx, (label, value, accent) in enumerate(metrics):
        row = idx // 3
        col = idx % 3
        x = start_x + col * (card_w + gap)
        y = 1.2 + row * (card_h + gap)
        card = _add_rounded_card(slide2, x, y, card_w, card_h, _CARD_BG)
        # Accent top bar
        _add_rounded_card(slide2, x, y, card_w, 0.06, accent)
        _add_textbox(slide2, x + 0.3, y + 0.25, card_w - 0.6, 0.4, label, font_size=13, color=_TEXT_SECONDARY)
        _add_textbox(slide2, x + 0.3, y + 0.7, card_w - 0.6, 0.7, value, font_size=26, bold=True, color=_TEXT_PRIMARY)

    # Summary interpretation
    qs = scan_info.get("quality_score", 0)
    if qs >= 90:
        summary_text = "Overall data quality is excellent. The dataset is well-suited for analysis with minimal preprocessing needed."
    elif qs >= 70:
        summary_text = "Data quality is good but some issues exist. Addressing missing values and duplicates will improve reliability."
    elif qs >= 50:
        summary_text = "Data quality is moderate. Significant cleaning is recommended before proceeding with analysis or modeling."
    else:
        summary_text = "Data quality is poor. Extensive cleaning and validation is required before this dataset can be used reliably."
    _add_textbox(slide2, 0.6, 5.0, 12, 1.2, f"Assessment: {summary_text}", font_size=13, color=_TEXT_SECONDARY)

    # ──────────────────────────────────────────────────────
    # SLIDE 3 — Column Profiles Table
    # ──────────────────────────────────────────────────────
    slide3 = prs.slides.add_slide(blank_layout)
    _set_slide_bg(slide3, _BG_DARK)
    _add_textbox(slide3, 0.6, 0.3, 12, 0.6, "Column Profiles", font_size=28, bold=True, color=_TEXT_PRIMARY)
    _add_rounded_card(slide3, 0.6, 0.85, 12, 0.04, _ACCENT)

    col_profiles = scan_info.get("columns", [])
    # Build table: limit to first 15 columns for slide readability
    display_profiles = col_profiles[:15]
    n_rows = len(display_profiles) + 1  # header + data
    n_cols_table = 6
    table_shape = slide3.shapes.add_table(
        n_rows, n_cols_table,
        Inches(0.6), Inches(1.1), Inches(12), Inches(min(n_rows * 0.45, 5.8))
    )
    table = table_shape.table
    headers = ["Column", "Type", "Non-Null", "Missing %", "Unique", "Outliers"]
    for ci, h in enumerate(headers):
        cell = table.cell(0, ci)
        cell.text = h
        for paragraph in cell.text_frame.paragraphs:
            paragraph.font.size = Pt(11)
            paragraph.font.bold = True
            paragraph.font.color.rgb = RGBColor.from_string(_TEXT_PRIMARY)
            paragraph.font.name = "Calibri"
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor.from_string(_ACCENT)

    for ri, cp in enumerate(display_profiles):
        row_data = [
            cp.get("name", ""),
            cp.get("dtype", ""),
            str(cp.get("non_null_count", "")),
            f"{cp.get('null_percentage', 0):.1f}%",
            str(cp.get("unique_count", "")),
            str(cp.get("outlier_count", "—") if cp.get("outlier_count") is not None else "—"),
        ]
        for ci, val in enumerate(row_data):
            cell = table.cell(ri + 1, ci)
            cell.text = val
            for paragraph in cell.text_frame.paragraphs:
                paragraph.font.size = Pt(10)
                paragraph.font.color.rgb = RGBColor.from_string(_TEXT_PRIMARY)
                paragraph.font.name = "Calibri"
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor.from_string(_CARD_BG if ri % 2 == 0 else _BG_DARK)

    if len(col_profiles) > 15:
        _add_textbox(slide3, 0.6, 6.8, 12, 0.4,
                     f"Showing 15 of {len(col_profiles)} columns. Full details available in the HTML audit report.",
                     font_size=10, color=_TEXT_SECONDARY)

    # ──────────────────────────────────────────────────────
    # SLIDE 4 — Correlation Heatmap + Implications
    # ──────────────────────────────────────────────────────
    corr_chart, corr_summary = _build_correlation_analysis(df)
    if corr_chart is not None:
        slide4 = prs.slides.add_slide(blank_layout)
        _set_slide_bg(slide4, _BG_DARK)
        _add_textbox(slide4, 0.6, 0.3, 12, 0.6, "Correlation Heatmap", font_size=28, bold=True, color=_TEXT_PRIMARY)
        _add_rounded_card(slide4, 0.6, 0.85, 12, 0.04, _ACCENT)

        try:
            img_bytes = _generate_chart_image(corr_chart, width=700, height=500)
            img_stream = BytesIO(img_bytes)
            slide4.shapes.add_picture(img_stream, Inches(0.6), Inches(1.1), Inches(7), Inches(5))
        except Exception:
            _add_textbox(slide4, 0.6, 1.1, 7, 5, "[Chart rendering unavailable]", font_size=14, color=_TEXT_SECONDARY)

        # Implications panel
        _add_rounded_card(slide4, 8.0, 1.1, 4.8, 5, _CARD_BG)
        _add_textbox(slide4, 8.2, 1.2, 4.4, 0.5, "What This Implies", font_size=16, bold=True, color=_ACCENT2)
        _add_textbox(slide4, 8.2, 1.75, 4.4, 4.2, corr_summary, font_size=11, color=_TEXT_PRIMARY)

    # ──────────────────────────────────────────────────────
    # SLIDE 5 — Numeric Distribution + Implications
    # ──────────────────────────────────────────────────────
    num_chart, num_summary, num_col = _build_numeric_distribution(df)
    if num_chart is not None:
        slide5 = prs.slides.add_slide(blank_layout)
        _set_slide_bg(slide5, _BG_DARK)
        _add_textbox(slide5, 0.6, 0.3, 12, 0.6, f"Distribution Analysis: {num_col}", font_size=28, bold=True, color=_TEXT_PRIMARY)
        _add_rounded_card(slide5, 0.6, 0.85, 12, 0.04, _GREEN)

        try:
            img_bytes = _generate_chart_image(num_chart, width=700, height=500)
            img_stream = BytesIO(img_bytes)
            slide5.shapes.add_picture(img_stream, Inches(0.6), Inches(1.1), Inches(7), Inches(5))
        except Exception:
            _add_textbox(slide5, 0.6, 1.1, 7, 5, "[Chart rendering unavailable]", font_size=14, color=_TEXT_SECONDARY)

        _add_rounded_card(slide5, 8.0, 1.1, 4.8, 5, _CARD_BG)
        _add_textbox(slide5, 8.2, 1.2, 4.4, 0.5, "What This Implies", font_size=16, bold=True, color=_GREEN)
        _add_textbox(slide5, 8.2, 1.75, 4.4, 4.2, num_summary, font_size=11, color=_TEXT_PRIMARY)

    # ──────────────────────────────────────────────────────
    # SLIDE 6 — Categorical Distribution + Implications
    # ──────────────────────────────────────────────────────
    cat_chart, cat_summary, cat_col = _build_categorical_distribution(df)
    if cat_chart is not None:
        slide6 = prs.slides.add_slide(blank_layout)
        _set_slide_bg(slide6, _BG_DARK)
        _add_textbox(slide6, 0.6, 0.3, 12, 0.6, f"Category Analysis: {cat_col}", font_size=28, bold=True, color=_TEXT_PRIMARY)
        _add_rounded_card(slide6, 0.6, 0.85, 12, 0.04, _PURPLE)

        try:
            img_bytes = _generate_chart_image(cat_chart, width=700, height=500)
            img_stream = BytesIO(img_bytes)
            slide6.shapes.add_picture(img_stream, Inches(0.6), Inches(1.1), Inches(7), Inches(5))
        except Exception:
            _add_textbox(slide6, 0.6, 1.1, 7, 5, "[Chart rendering unavailable]", font_size=14, color=_TEXT_SECONDARY)

        _add_rounded_card(slide6, 8.0, 1.1, 4.8, 5, _CARD_BG)
        _add_textbox(slide6, 8.2, 1.2, 4.4, 0.5, "What This Implies", font_size=16, bold=True, color=_PURPLE)
        _add_textbox(slide6, 8.2, 1.75, 4.4, 4.2, cat_summary, font_size=11, color=_TEXT_PRIMARY)

    # ──────────────────────────────────────────────────────
    # SLIDE 7 — Purification Audit Log
    # ──────────────────────────────────────────────────────
    if len(history) > 1:
        slide7 = prs.slides.add_slide(blank_layout)
        _set_slide_bg(slide7, _BG_DARK)
        _add_textbox(slide7, 0.6, 0.3, 12, 0.6, "Purification Audit Log", font_size=28, bold=True, color=_TEXT_PRIMARY)
        _add_rounded_card(slide7, 0.6, 0.85, 12, 0.04, _ACCENT)

        ops = [h for h in history if h.get("operation") != "upload"]
        display_ops = ops[:12]
        n_rows_h = len(display_ops) + 1
        tbl_shape = slide7.shapes.add_table(
            n_rows_h, 4,
            Inches(0.6), Inches(1.1), Inches(12), Inches(min(n_rows_h * 0.5, 5.8))
        )
        tbl = tbl_shape.table
        for ci, h in enumerate(["#", "Operation", "Description", "Rows Affected"]):
            cell = tbl.cell(0, ci)
            cell.text = h
            for paragraph in cell.text_frame.paragraphs:
                paragraph.font.size = Pt(11)
                paragraph.font.bold = True
                paragraph.font.color.rgb = RGBColor.from_string(_TEXT_PRIMARY)
                paragraph.font.name = "Calibri"
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor.from_string(_ACCENT)

        for ri, op in enumerate(display_ops):
            row_data = [
                str(op.get("index", ri + 1)),
                op.get("operation", ""),
                op.get("description", ""),
                str(op.get("rows_affected", "")),
            ]
            for ci, val in enumerate(row_data):
                cell = tbl.cell(ri + 1, ci)
                cell.text = val
                for paragraph in cell.text_frame.paragraphs:
                    paragraph.font.size = Pt(10)
                    paragraph.font.color.rgb = RGBColor.from_string(_TEXT_PRIMARY)
                    paragraph.font.name = "Calibri"
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor.from_string(_CARD_BG if ri % 2 == 0 else _BG_DARK)

        if len(ops) > 12:
            _add_textbox(slide7, 0.6, 6.8, 12, 0.4,
                         f"Showing 12 of {len(ops)} operations.",
                         font_size=10, color=_TEXT_SECONDARY)

    # Save to bytes
    output = BytesIO()
    prs.save(output)
    return output.getvalue()

