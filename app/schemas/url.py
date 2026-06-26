from pydantic import BaseModel, Field, HttpUrl, field_validator
from typing import Optional, Dict, Any
from datetime import datetime
import re


class URLCreateRequest(BaseModel):

    url: str = Field(..., description="The original URL to shorten")
    custom_alias: Optional[str] = Field(
        None,
        min_length=3,
        max_length=20,
        description="Optional custom alias (alphanumeric + hyphen, 3-20 chars)",
    )
    expiry_date: Optional[datetime] = Field(
        None, description="Optional expiration datetime (ISO 8601)"
    )
    url_type: Optional[str] = Field(
        "302", description="Redirect type: '301' (permanent) or '302' (temporary)"
    )

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        if len(v) > 2048:
            raise ValueError("URL must be less than 2048 characters")
        return v

    @field_validator("custom_alias")
    @classmethod
    def validate_alias(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not re.match(r"^[a-zA-Z0-9\-]{3,20}$", v):
                raise ValueError(
                    "Alias must be 3-20 characters, alphanumeric and hyphens only"
                )
        return v

    @field_validator("url_type")
    @classmethod
    def validate_url_type(cls, v: str) -> str:
        if v not in ("301", "302"):
            raise ValueError("url_type must be '301' or '302'")
        return v


class URLResponse(BaseModel):

    id: int
    short_code: str
    short_url: str
    long_url: str
    created_at: datetime
    expiry_date: Optional[datetime] = None
    url_type: str = "302"
    safety_score: float = 1.0
    warnings: Optional[Dict[str, Any]] = None
    has_warnings: bool = False

    model_config = {"from_attributes": True}


class URLInfoResponse(BaseModel):

    short_code: str
    long_url: str
    created_at: datetime
    expiry_date: Optional[datetime] = None
    click_count: int = 0
    is_active: bool = True
    url_type: str = "302"
    safety_score: float = 1.0

    model_config = {"from_attributes": True}


class ErrorResponse(BaseModel):

    error: str
    detail: str
    code: int
