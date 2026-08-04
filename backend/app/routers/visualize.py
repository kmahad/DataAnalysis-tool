"""
Visualize Router — Generates charts based on current session data.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.models.schemas import ChartRequest, ChartResponse
from app.models.session import session_manager
from app.routers.auth import get_current_user
from app.services.visualizer import generate_chart

router = APIRouter(prefix="/api/visualize", tags=["visualize"])


@router.post("", response_model=ChartResponse)
async def build_chart(
    req: ChartRequest,
    current_user: str = Depends(get_current_user),
):
    session = session_manager.get_session(req.session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{req.session_id}' not found.",
        )

    try:
        chart_dict = generate_chart(
            df=session.df,
            chart_type=req.chart_type.value,
            x_column=req.x_column,
            y_column=req.y_column,
            color_column=req.color_column,
            title=req.title,
            aggregation=req.aggregation,
        )
        return ChartResponse(chart_json=chart_dict)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to generate chart: {str(e)}",
        )
