"""
Visualization Service — Generates Plotly chart specifications as JSON.
"""

from typing import Any, Optional
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def generate_chart(
    df: pd.DataFrame,
    chart_type: str,
    x_column: Optional[str] = None,
    y_column: Optional[str] = None,
    color_column: Optional[str] = None,
    title: Optional[str] = None,
    aggregation: Optional[str] = None,
) -> dict[str, Any]:
    """Generate a Plotly chart figure dict based on requested chart parameters."""
    chart_df = df.copy()

    # Apply aggregation if requested (e.g. for bar charts)
    if aggregation and x_column:
        if y_column:
            if aggregation == "sum":
                chart_df = chart_df.groupby([x_column] + ([color_column] if color_column else []))[y_column].sum().reset_index()
            elif aggregation == "mean":
                chart_df = chart_df.groupby([x_column] + ([color_column] if color_column else []))[y_column].mean().reset_index()
            elif aggregation == "count":
                chart_df = chart_df.groupby([x_column] + ([color_column] if color_column else []))[y_column].count().reset_index()
            elif aggregation == "median":
                chart_df = chart_df.groupby([x_column] + ([color_column] if color_column else []))[y_column].median().reset_index()
        else:
            if aggregation == "count":
                chart_df = chart_df.groupby(x_column).size().reset_index(name="count")
                y_column = "count"

    # Dark theme template styling
    dark_layout_defaults = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(18,18,26,0.7)",
        font=dict(color="#e2e8f0", family="Inter, sans-serif"),
        title=dict(text=title or f"{chart_type.title()} Chart", font=dict(size=18, color="#f8fafc")),
        margin=dict(l=40, r=40, t=50, b=40),
        xaxis=dict(gridcolor="#2d3748", zerolinecolor="#4a5568"),
        yaxis=dict(gridcolor="#2d3748", zerolinecolor="#4a5568"),
    )

    if chart_type == "bar":
        fig = px.bar(
            chart_df,
            x=x_column,
            y=y_column,
            color=color_column,
            title=title or f"Bar Chart: {y_column or 'Count'} by {x_column}",
            template="plotly_dark",
        )
    elif chart_type == "line":
        fig = px.line(
            chart_df,
            x=x_column,
            y=y_column,
            color=color_column,
            title=title or f"Line Chart: {y_column} over {x_column}",
            template="plotly_dark",
        )
    elif chart_type == "scatter":
        fig = px.scatter(
            chart_df,
            x=x_column,
            y=y_column,
            color=color_column,
            title=title or f"Scatter Plot: {y_column} vs {x_column}",
            template="plotly_dark",
        )
    elif chart_type == "pie":
        fig = px.pie(
            chart_df,
            names=x_column,
            values=y_column,
            title=title or f"Pie Chart: {x_column}",
            template="plotly_dark",
        )
    elif chart_type == "histogram":
        fig = px.histogram(
            chart_df,
            x=x_column,
            color=color_column,
            title=title or f"Histogram: Distribution of {x_column}",
            template="plotly_dark",
        )
    elif chart_type == "box":
        fig = px.box(
            chart_df,
            x=x_column,
            y=y_column,
            color=color_column,
            title=title or f"Box Plot: {y_column or x_column}",
            template="plotly_dark",
        )
    elif chart_type == "violin":
        fig = px.violin(
            chart_df,
            x=x_column,
            y=y_column,
            color=color_column,
            box=True,
            title=title or f"Violin Plot: {y_column or x_column}",
            template="plotly_dark",
        )
    elif chart_type == "heatmap":
        numeric_df = chart_df.select_dtypes(include=["number"])
        corr = numeric_df.corr()
        fig = px.imshow(
            corr,
            text_auto=".2f",
            aspect="auto",
            title=title or "Correlation Heatmap",
            color_continuous_scale="Viridis",
            template="plotly_dark",
        )
    else:
        raise ValueError(f"Unsupported chart type: {chart_type}")

    fig.update_layout(**dark_layout_defaults)
    return json.loads(fig.to_json())
