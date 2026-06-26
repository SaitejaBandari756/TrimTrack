from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    Index,
    ForeignKey,
)
from sqlalchemy import DateTime
from sqlalchemy.sql import func
from app.database.session import Base


class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    short_code = Column(
        String(20),
        ForeignKey("urls.short_code", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    clicked_at = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String(45), nullable=True)  # IPv4/IPv6 string
    user_agent = Column(Text, nullable=True)
    country = Column(String(100), nullable=True)
    is_unique = Column(Boolean, default=False, nullable=False)

    __table_args__ = (
        Index("idx_analytics_short_code", "short_code"),
        Index("idx_analytics_clicked_at", "clicked_at"),
        Index("idx_analytics_unique", "short_code", "ip_address"),
    )

    def __repr__(self):
        return f"<Analytics(short_code={self.short_code}, country={self.country}, is_unique={self.is_unique})>"
