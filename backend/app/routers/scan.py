"""
Scan Router — Triggers full data scanning and profiling for a session.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.models.schemas import DataPreviewResponse, ScanReport
from app.models.session import session_manager
from app.routers.auth import get_current_user
from app.services.scanner import scan_dataframe

router = APIRouter(prefix="/api/scan", tags=["scan"])


@router.get("/{session_id}", response_model=ScanReport)
async def scan_data(
    session_id: str,
    current_user: str = Depends(get_current_user),
):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )

    report_dict = scan_dataframe(session.df, session_id)
    return ScanReport(**report_dict)


@router.get("/{session_id}/preview", response_model=DataPreviewResponse)
async def get_data_preview(
    session_id: str,
    page: int = 1,
    page_size: int = 50,
    current_user: str = Depends(get_current_user),
):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )

    df = session.df
    total_rows = len(df)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size

    paged_df = df.iloc[start_idx:end_idx].fillna("").copy()
    data = paged_df.to_dict(orient="records")
    col_types = {col: str(df[col].dtype) for col in df.columns}

    return DataPreviewResponse(
        session_id=session_id,
        rows=paged_df.shape[0],
        columns=df.shape[1],
        column_names=list(df.columns),
        column_types=col_types,
        data=data,
        total_rows=total_rows,
    )
