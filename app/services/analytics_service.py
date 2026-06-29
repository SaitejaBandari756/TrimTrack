import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from collections import defaultdict
from sqlalchemy import select, func, and_, literal_column
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.analytics import Analytics
from app.models.url import URL
from app.schemas.analytics import ClickEvent, AnalyticsResponse, LiveClickUpdate
from app.utils.geo_lookup import lookup_country

logger = logging.getLogger(__name__)
_ws_connections: dict[str, list] = defaultdict(list)


def _is_sqlite(session: AsyncSession) -> bool:
    try:
        return "sqlite" in str(session.get_bind().url)
    except Exception:
        pass
    try:
        return "sqlite" in str(session.sync_session.bind.url)
    except Exception:
        pass
    try:
        from app.database.session import engine
        return "sqlite" in str(engine.url)
    except Exception:
        return False


class AnalyticsService:
    async def record_click(self, session: AsyncSession, short_code: str,
                           ip_address: Optional[str] = None, user_agent: Optional[str] = None):
        import traceback
        print(f"\n>>> [ANALYTICS DEBUG] record_click called for '{short_code}' from IP={ip_address}", flush=True)
        try:
            is_sqlite = _is_sqlite(session)
            print(f">>> [ANALYTICS DEBUG] is_sqlite={is_sqlite}", flush=True)

            country = await lookup_country(ip_address) if ip_address else "Unknown"
            print(f">>> [ANALYTICS DEBUG] country={country}", flush=True)

            is_unique = False
            if ip_address:
                existing = await session.execute(
                    select(Analytics.id).where(
                        and_(
                            Analytics.short_code == short_code,
                            Analytics.ip_address == ip_address
                        )
                    ).limit(1)
                )
                if existing.scalar_one_or_none() is None:
                    is_unique = True
            else:
                is_unique = True
            print(f">>> [ANALYTICS DEBUG] is_unique={is_unique}", flush=True)

            analytics = Analytics(
                short_code=short_code, ip_address=ip_address,
                user_agent=user_agent, country=country, is_unique=is_unique
            )
            session.add(analytics)
            print(">>> [ANALYTICS DEBUG] analytics row added", flush=True)

            stmt = select(URL).where(URL.short_code == short_code)
            if not is_sqlite:
                stmt = stmt.with_for_update()
            result = await session.execute(stmt)
            url = result.scalar_one_or_none()
            print(f">>> [ANALYTICS DEBUG] url found={url is not None}, current count={url.click_count if url else 'N/A'}", flush=True)
            if url:
                url.click_count = (url.click_count or 0) + 1
                print(f">>> [ANALYTICS DEBUG] click_count set to {url.click_count}", flush=True)

            await session.commit()
            print(f">>> [ANALYTICS DEBUG] commit successful! Final count={url.click_count if url else 'N/A'}", flush=True)

            await self._notify_ws(short_code, ClickEvent(
                short_code=short_code, clicked_at=datetime.now(timezone.utc),
                ip_address=ip_address, user_agent=user_agent, country=country,
            ), url.click_count if url else 0)

        except Exception as e:
            print(f"\n>>> [ANALYTICS ERROR] FAILED: {e}", flush=True)
            print(">>> [ANALYTICS ERROR] Full traceback:", flush=True)
            traceback.print_exc()
            try:
                await session.rollback()
                print(">>> [ANALYTICS ERROR] rollback done", flush=True)
            except Exception as rb_err:
                print(f">>> [ANALYTICS ERROR] rollback also failed: {rb_err}", flush=True)

    async def get_analytics(self, session: AsyncSession, short_code: str) -> Optional[AnalyticsResponse]:
        url_result = await session.execute(select(URL).where(URL.short_code == short_code))
        url = url_result.scalar_one_or_none()
        if not url:
            return None

        country_stmt = (select(Analytics.country, func.count(Analytics.id))
                        .where(Analytics.short_code == short_code)
                        .group_by(Analytics.country).order_by(func.count(Analytics.id).desc()))
        country_result = await session.execute(country_stmt)
        country_breakdown = {row[0] or "Unknown": row[1] for row in country_result.fetchall()}

        unique_stmt = (select(func.count(Analytics.id))
                       .where(and_(Analytics.short_code == short_code, Analytics.is_unique)))
        unique_result = await session.execute(unique_stmt)
        unique_clicks = unique_result.scalar() or 0

        hourly_trend = []
        try:
            now = datetime.now(timezone.utc)
            day_ago = now - timedelta(hours=24)

            using_sqlite = _is_sqlite(session)

            if using_sqlite:
                hourly_stmt = (
                    select(
                        func.strftime('%Y-%m-%dT%H:00:00', Analytics.clicked_at).label("hour"),
                        func.count(Analytics.id).label("clicks")
                    )
                    .where(Analytics.short_code == short_code, Analytics.clicked_at >= day_ago)
                    .group_by(literal_column("hour")).order_by(literal_column("hour"))
                )
            else:
                hourly_stmt = (
                    select(
                        func.date_trunc("hour", Analytics.clicked_at).label("hour"),
                        func.count(Analytics.id).label("clicks")
                    )
                    .where(Analytics.short_code == short_code, Analytics.clicked_at >= day_ago)
                    .group_by("hour").order_by("hour")
                )

            hourly_result = await session.execute(hourly_stmt)
            hourly_trend = [{"hour": str(row[0]), "clicks": row[1]} for row in hourly_result.fetchall()]
        except Exception as e:
            logger.warning(f"Hourly trend query failed: {e}")

        daily_trend = []
        try:
            now = datetime.now(timezone.utc)
            month_ago = now - timedelta(days=30)

            using_sqlite = _is_sqlite(session)

            if using_sqlite:
                daily_stmt = (
                    select(
                        func.strftime('%Y-%m-%d', Analytics.clicked_at).label("date"),
                        func.count(Analytics.id).label("clicks")
                    )
                    .where(Analytics.short_code == short_code, Analytics.clicked_at >= month_ago)
                    .group_by(literal_column("date")).order_by(literal_column("date"))
                )
            else:
                daily_stmt = (
                    select(
                        func.date_trunc("day", Analytics.clicked_at).label("date"),
                        func.count(Analytics.id).label("clicks")
                    )
                    .where(Analytics.short_code == short_code, Analytics.clicked_at >= month_ago)
                    .group_by("date").order_by("date")
                )

            daily_result = await session.execute(daily_stmt)
            daily_trend = [{"date": str(row[0])[:10], "clicks": row[1]} for row in daily_result.fetchall()]
        except Exception as e:
            logger.warning(f"Daily trend query failed: {e}")

        recent_stmt = (select(Analytics).where(Analytics.short_code == short_code)
                       .order_by(Analytics.clicked_at.desc()).limit(20))
        recent_result = await session.execute(recent_stmt)
        recent_clicks = [ClickEvent(short_code=a.short_code, clicked_at=a.clicked_at,
                                    ip_address=a.ip_address, user_agent=a.user_agent, country=a.country)
                         for a in recent_result.scalars().all()]

        return AnalyticsResponse(
            short_code=short_code,
            total_clicks=url.click_count or 0,
            unique_clicks=unique_clicks,
            country_breakdown=country_breakdown,
            hourly_trend=hourly_trend,
            daily_trend=daily_trend,
            recent_clicks=recent_clicks,
        )

    def register_ws(self, short_code: str, websocket):
        _ws_connections[short_code].append(websocket)

    def unregister_ws(self, short_code: str, websocket):
        if short_code in _ws_connections:
            _ws_connections[short_code] = [ws for ws in _ws_connections[short_code] if ws != websocket]
            if not _ws_connections[short_code]:
                del _ws_connections[short_code]

    async def _notify_ws(self, short_code: str, click_event: ClickEvent, total_clicks: int):
        if short_code not in _ws_connections:
            return
        update = LiveClickUpdate(short_code=short_code, total_clicks=total_clicks,
                                 latest_click=click_event, timestamp=datetime.now(timezone.utc))
        dead_ws = []
        for ws in _ws_connections[short_code]:
            try:
                await ws.send_json(update.model_dump(mode="json"))
            except Exception:
                dead_ws.append(ws)
        for ws in dead_ws:
            self.unregister_ws(short_code, ws)

analytics_service = AnalyticsService()