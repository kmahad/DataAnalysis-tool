"""
Database Connector Service — Connects to databases via SQLAlchemy connection strings.
"""

from typing import Any, Optional
import pandas as pd
from sqlalchemy import create_engine, inspect, text


def get_engine(connection_string: str):
    """Create SQLAlchemy engine with safe parameters."""
    return create_engine(connection_string, pool_pre_ping=True)


def list_tables(connection_string: str) -> list[str]:
    """List table names available in the connected database."""
    engine = get_engine(connection_string)
    inspector = inspect(engine)
    return inspector.get_table_names()


def load_from_db(
    connection_string: str,
    query: Optional[str] = None,
    table_name: Optional[str] = None,
    limit: int = 100000,
) -> tuple[pd.DataFrame, str]:
    """Load data from database into a pandas DataFrame. Returns (df, source_description)."""
    engine = get_engine(connection_string)

    if query:
        # Wrap custom query with limit if not already present
        clean_query = query.strip().rstrip(";")
        if "LIMIT" not in clean_query.upper():
            sql = f"{clean_query} LIMIT {limit}"
        else:
            sql = clean_query
        df = pd.read_sql(text(sql), engine)
        desc = f"SQL Query result ({len(df)} rows)"
    elif table_name:
        sql = f"SELECT * FROM {table_name} LIMIT {limit}"
        df = pd.read_sql(text(sql), engine)
        desc = f"Table '{table_name}' ({len(df)} rows)"
    else:
        raise ValueError("Either query or table_name must be provided")

    return df, desc
