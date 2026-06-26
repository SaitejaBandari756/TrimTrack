from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime


class ClickEvent(BaseModel):

    short_code: str
    clicked_at: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    country: Optional[str] = None

    model_config = {"from_attributes": True}


class AnalyticsResponse(BaseModel):

    short_code: str
    total_clicks: int
    unique_clicks: int = 0
    country_breakdown: Dict[str, int]
    hourly_trend: List[Dict[str, object]]
    daily_trend: List[Dict[str, object]] = []
    recent_clicks: List[ClickEvent]


class LiveClickUpdate(BaseModel):

    short_code: str
    total_clicks: int
    latest_click: Optional[ClickEvent] = None
    timestamp: datetime
