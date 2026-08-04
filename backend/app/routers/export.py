"""
Export Router — Download cleaned data as CSV, Excel, or HTML audit report.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, Response

from app.models.schemas import ExportFormat, ExportRequest
from app.models.session import session_manager
from app.routers.auth import get_current_user
from app.services.exporter import export_to_csv, export_to_excel, export_to_html_report
from app.services.scanner import scan_dataframe

router = APIRouter(prefix="/api/export", tags=["export"])


@router.post("")
async def export_data(
    req: ExportRequest,
    current_user: str = Depends(get_current_user),
):
    session = session_manager.get_session(req.session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{req.session_id}' not found.",
        )

    filename_base = session.filename.rsplit(".", 1)[0]

    if req.format == ExportFormat.csv:
        csv_bytes = export_to_csv(session.df, req.include_columns)
        return Response(
            content=csv_bytes,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename_base}_purified.csv"},
        )

    elif req.format == ExportFormat.excel:
        excel_bytes = export_to_excel(session.df, req.include_columns)
        return Response(
            content=excel_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename_base}_purified.xlsx"},
        )

    elif req.format == ExportFormat.html_report:
        scan_info = scan_dataframe(session.df, session.session_id)
        html_content = export_to_html_report(
            session_id=session.session_id,
            df=session.df,
            filename=session.filename,
            history=session.get_history(),
            scan_info=scan_info,
        )
        return HTMLResponse(content=html_content)

    else:
        raise HTTPException(status_code=400, detail="Invalid export format")
