from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Text,
    Boolean,
    Float,
    Index,
)
from sqlalchemy import DateTime
from sqlalchemy.sql import func
from app.database.session import Base


class URL(Base):
    __tablename__ = "urls"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=False)
    short_code = Column(String(20), unique=True, nullable=False, index=True)
    long_url = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expiry_date = Column(DateTime(timezone=True), nullable=True)
    click_count = Column(BigInteger, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    url_type = Column(String(10), default="302", nullable=False)
    safety_score = Column(Float, default=1.0, nullable=False)

    __table_args__ = (
        Index("idx_urls_short_code", "short_code"),
        Index("idx_urls_active", "is_active"),
    )

    def __repr__(self):
        return f"<URL(short_code={self.short_code}, long_url={self.long_url[:50]})>"