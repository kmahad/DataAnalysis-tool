"""
File Upload Router — Handles CSV and Excel file uploads.
"""

from io import BytesIO
from typing import Any
import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.models.schemas import UploadResponse
from app.models.session import session_manager
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/upload", tags=["upload"])


@router.post("", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user),
):
    filename = file.filename or "uploaded_file"
    contents = await file.read()

    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(BytesIO(contents))
        elif filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(BytesIO(contents))
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file format. Please upload CSV or Excel (.xlsx, .xls) files.",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse data file: {str(e)}",
        )

    # Clean up column names (strip whitespace)
    df.columns = [str(col).strip() for col in df.columns]

    # Create session
    session = session_manager.create_session(df, filename)

    preview_df = df.head(50).fillna("").copy()
    # Convert dataframe to JSON-compatible preview list
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
