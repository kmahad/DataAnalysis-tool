"""
Clean Router — Handles all 6 data purification operations, plus undo/redo history navigation.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.models.schemas import (
    CleanStringsRequest,
    CleaningResult,
    ColumnOperationsRequest,
    ConvertTypesRequest,
    HandleMissingRequest,
    HandleOutliersRequest,
    HistoryResponse,
    RemoveDuplicatesRequest,
)
from app.models.session import session_manager
from app.routers.auth import get_current_user
from app.services.purifier import (
    clean_strings,
    column_operations,
    convert_types,
    handle_missing_values,
    handle_outliers,
    remove_duplicates,
)

router = APIRouter(prefix="/api/clean", tags=["clean"])


def _get_session_or_404(session_id: str):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )
    return session


def _build_result(session, operation: str, desc: str, new_df, affected_rows: int, affected_cols: list[str]) -> CleaningResult:
    rows_before = session.df.shape[0]
    cols_before = session.df.shape[1]

    history_idx = session.push_state(
        operation=operation,
        description=desc,
        new_df=new_df,
        rows_affected=affected_rows,
        columns_affected=affected_cols,
    )

    preview_df = session.df.head(50).fillna("").copy()
    preview = preview_df.to_dict(orient="records")

    return CleaningResult(
        session_id=session.session_id,
        operation=operation,
        description=desc,
        rows_before=rows_before,
        rows_after=session.df.shape[0],
        columns_before=cols_before,
        columns_after=session.df.shape[1],
        rows_affected=affected_rows,
        columns_affected=affected_cols,
        timestamp=session.history[history_idx].timestamp,
        history_index=history_idx,
        preview=preview,
    )


@router.post("/missing", response_model=CleaningResult)
async def clean_missing_values(req: HandleMissingRequest, current_user: str = Depends(get_current_user)):
    session = _get_session_or_404(req.session_id)
    new_df, desc, affected = handle_missing_values(
        df=session.df,
        columns=req.columns,
        strategy=req.strategy.value,
        fill_value=req.fill_value,
        threshold=req.threshold,
    )
    return _build_result(session, "handle_missing", desc, new_df, affected, req.columns)


@router.post("/duplicates", response_model=CleaningResult)
async def clean_duplicates(req: RemoveDuplicatesRequest, current_user: str = Depends(get_current_user)):
    session = _get_session_or_404(req.session_id)
    new_df, desc, affected = remove_duplicates(
        df=session.df,
        subset_columns=req.subset_columns,
        keep=req.keep.value,
    )
    cols = req.subset_columns or list(session.df.columns)
    return _build_result(session, "remove_duplicates", desc, new_df, affected, cols)


@router.post("/outliers", response_model=CleaningResult)
async def clean_outliers(req: HandleOutliersRequest, current_user: str = Depends(get_current_user)):
    session = _get_session_or_404(req.session_id)
    new_df, desc, affected = handle_outliers(
        df=session.df,
        columns=req.columns,
        method=req.method.value,
        action=req.action.value,
        threshold=req.threshold,
    )
    return _build_result(session, "handle_outliers", desc, new_df, affected, req.columns)


@router.post("/types", response_model=CleaningResult)
async def clean_types(req: ConvertTypesRequest, current_user: str = Depends(get_current_user)):
    session = _get_session_or_404(req.session_id)
    new_df, desc, affected = convert_types(
        df=session.df,
        conversions=req.conversions,
        datetime_format=req.datetime_format,
    )
    return _build_result(session, "convert_types", desc, new_df, affected, list(req.conversions.keys()))


@router.post("/strings", response_model=CleaningResult)
async def clean_string_columns(req: CleanStringsRequest, current_user: str = Depends(get_current_user)):
    session = _get_session_or_404(req.session_id)
    actions = [a.value for a in req.actions]
    new_df, desc, affected = clean_strings(
        df=session.df,
        columns=req.columns,
        actions=actions,
        regex_pattern=req.regex_pattern,
        regex_replacement=req.regex_replacement,
    )
    return _build_result(session, "clean_strings", desc, new_df, affected, req.columns)


@router.post("/columns", response_model=CleaningResult)
async def clean_columns(req: ColumnOperationsRequest, current_user: str = Depends(get_current_user)):
    session = _get_session_or_404(req.session_id)
    new_df, desc, affected = column_operations(
        df=session.df,
        action=req.action.value,
        rename_map=req.rename_map,
        drop_columns=req.drop_columns,
        new_order=req.new_order,
    )
    cols = list(req.rename_map.keys()) if req.rename_map else (req.drop_columns or req.new_order or [])
    return _build_result(session, "column_operations", desc, new_df, affected, cols)


# ─── History & Undo / Redo ──────────────────────────────────────────
@router.get("/history/{session_id}", response_model=HistoryResponse)
async def get_history(session_id: str, current_user: str = Depends(get_current_user)):
    session = _get_session_or_404(session_id)
    return HistoryResponse(
        session_id=session_id,
        entries=session.get_history(),
        current_index=session.current_index,
        can_undo=session.can_undo,
        can_redo=session.can_redo,
    )


@router.post("/undo/{session_id}", response_model=HistoryResponse)
async def undo_operation(session_id: str, current_user: str = Depends(get_current_user)):
    session = _get_session_or_404(session_id)
    restored = session.undo()
    if restored is None:
        raise HTTPException(status_code=400, detail="Cannot undo further.")
    return HistoryResponse(
        session_id=session_id,
        entries=session.get_history(),
        current_index=session.current_index,
        can_undo=session.can_undo,
        can_redo=session.can_redo,
    )


@router.post("/redo/{session_id}", response_model=HistoryResponse)
async def redo_operation(session_id: str, current_user: str = Depends(get_current_user)):
    session = _get_session_or_404(session_id)
    restored = session.redo()
    if restored is None:
        raise HTTPException(status_code=400, detail="Cannot redo further.")
    return HistoryResponse(
        session_id=session_id,
        entries=session.get_history(),
        current_index=session.current_index,
        can_undo=session.can_undo,
        can_redo=session.can_redo,
    )


@router.post("/jump/{session_id}/{index}", response_model=HistoryResponse)
async def jump_to_history(session_id: str, index: int, current_user: str = Depends(get_current_user)):
    session = _get_session_or_404(session_id)
    restored = session.jump_to(index)
    if restored is None:
        raise HTTPException(status_code=400, detail="Invalid history index.")
    return HistoryResponse(
        session_id=session_id,
        entries=session.get_history(),
        current_index=session.current_index,
        can_undo=session.can_undo,
        can_redo=session.can_redo,
    )
