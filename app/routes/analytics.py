from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_session
from app.services.analytics_service import analytics_service

router = APIRouter()


@router.get("/analytics/{short_code}", tags=["Analytics"])
async def get_analytics(short_code: str, session: AsyncSession = Depends(get_session)):
    result = await analytics_service.get_analytics(session, short_code)
    if not result:
        return JSONResponse(
            status_code=404,
            content={
                "error": "Not Found",
                "detail": f"No analytics for '{short_code}'",
                "code": 404,
            },
        )
    return result


@router.websocket("/ws/analytics/{short_code}")
async def websocket_analytics(websocket: WebSocket, short_code: str):
    await websocket.accept()
    analytics_service.register_ws(short_code, websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except WebSocketDisconnect:
        analytics_service.unregister_ws(short_code, websocket)
