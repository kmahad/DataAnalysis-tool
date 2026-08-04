"""
Database Router — Handles database connections, listing tables, and running queries.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.models.schemas import DatabaseConnectRequest, DatabaseTablesResponse, UploadResponse
from app.models.session import session_manager
from app.routers.auth import get_current_user
from app.services.db_connector import list_tables, load_from_db

router = APIRouter(prefix="/api/database", tags=["database"])


@router.post("/tables", response_model=DatabaseTablesResponse)
async def get_database_tables(
    req: DatabaseConnectRequest,
    current_user: str = Depends(get_current_user),
):
    try:
        tables = list_tables(req.connection_string)
        return DatabaseTablesResponse(tables=tables)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to connect or list tables: {str(e)}",
        )


@router.post("/load", response_model=UploadResponse)
async def load_database_data(
    req: DatabaseConnectRequest,
    current_user: str = Depends(get_current_user),
):
    try:
        df, desc = load_from_db(
            connection_string=req.connection_string,
            query=req.query,
            table_name=req.table_name,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to query database: {str(e)}",
        )

    filename = req.table_name or "db_query_result"
    session = session_manager.create_session(df, filename)

    preview_df = df.head(50).fillna("").copy()
    preview = preview_df.to_dict(orient="records")
    col_types = {col: str(df[col].dtype) for col in df.columns}

    return UploadResponse(
        session_id=session.session_id,
        filename=filename,
        rows=df.shape[0],
        columns=df.shape[1],
        column_names=list(df.columns),
        column_types=col_types,
        preview=preview,
    )
