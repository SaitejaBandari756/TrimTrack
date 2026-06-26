import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings
from app.middleware.logging import LoggingMiddleware, setup_logging
from app.middleware.rate_limit import RateLimitMiddleware
from app.routes import shorten, redirect, analytics, health, qr, landing
from app.services.cache_service import cache_service
from app.services.bloom_filter import bloom_filter_service
from app.database.session import init_engine, dispose_engine
from app.database.init_db import warm_cache
from app.utils.id_generator import init_id_generator
from app.utils.url_helpers import is_using_ngrok, get_public_base_url

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def cleanup_expired_urls():
    from app.database.session import async_session_factory
    from app.services.url_service import url_service
    async with async_session_factory() as session:
        count = await url_service.cleanup_expired(session)
        if count > 0:
            logger.info(f"Cleaned up {count} expired URLs")


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(settings.debug)
    logger.info(f"Starting {settings.app_name}...")

    init_id_generator(settings.machine_id)
    logger.info(f"Snowflake ID generator initialized (machine_id={settings.machine_id})")

    await init_engine()

    await cache_service.connect()

    bloom_filter_service.initialize()

    await warm_cache()

    scheduler.add_job(cleanup_expired_urls, "interval", hours=1, id="cleanup_expired")
    scheduler.start()
    logger.info("Background scheduler started")

    if is_using_ngrok():
        logger.info(f"✓ NGROK enabled! Public URL: {get_public_base_url()}")
        logger.info("  QR codes will work on mobile phones with this URL")
    else:
        logger.info(f"✓ Using local/configured base URL: {get_public_base_url()}")
        logger.info("  To use ngrok for mobile access, set NGROK_URL environment variable")

    logger.info(f"{settings.app_name} is ready! Base URL: {settings.base_url}")
    yield

    scheduler.shutdown(wait=False)
    await cache_service.disconnect()
    await dispose_engine()
    logger.info(f"{settings.app_name} shut down cleanly")


app = FastAPI(
    title="TrimTrack API",
    description="TrimTrack — Production-grade URL shortener with click analytics, QR generation, "
                "distributed ID generation, Redis caching, Bloom filters, and ML-based abuse detection.",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

app.include_router(landing.router)
app.include_router(shorten.router)
app.include_router(health.router)
app.include_router(qr.router)
app.include_router(analytics.router)
app.include_router(redirect.router)  
if settings.prometheus_enabled:
    try:
        from prometheus_fastapi_instrumentator import Instrumentator
        Instrumentator().instrument(app).expose(app, endpoint="/metrics")
    except ImportError:
        pass


@app.get("/dashboard/{short_code}", response_class=HTMLResponse, tags=["Dashboard"])
async def analytics_dashboard(short_code: str):
    """Serve the real-time analytics dashboard."""
    html = _get_dashboard_html(short_code)
    return HTMLResponse(content=html)


def _get_dashboard_html(short_code: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TrimTrack Analytics — {short_code}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"></script>
    <style>
        *{{margin:0;padding:0;box-sizing:border-box}}
        body{{font-family:'Inter',system-ui,-apple-system,sans-serif;background:linear-gradient(135deg,#0a0e27 0%,#1a1f3a 100%);color:#e0e0e0;min-height:100vh}}
        .container{{max-width:1200px;margin:0 auto;padding:2rem}}
        h1{{font-size:1.8rem;background:linear-gradient(135deg,#a855f7,#7c3aed,#d946ef);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:.5rem}}
        .subtitle{{color:#9090a8;font-size:.9rem;margin-bottom:2rem}}
        .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1.5rem;margin-bottom:2rem}}
        .card{{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:16px;padding:1.5rem;backdrop-filter:blur(12px);transition:border-color .3s,transform .3s}}
        .card:hover{{border-color:rgba(124,58,237,.4);transform:translateY(-2px)}}
        .card-label{{font-size:.75rem;text-transform:uppercase;letter-spacing:.1em;color:#9090a8;margin-bottom:.5rem}}
        .card-value{{font-size:2rem;font-weight:700;color:#fff}}
        .card-value.live{{color:#10b981}}
        .card-value.unique{{color:#a855f7}}
        .chart-container{{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:16px;padding:1.5rem;margin-bottom:2rem}}
        .chart-title{{font-size:1rem;color:#ccc;margin-bottom:1rem;display:flex;align-items:center;gap:.5rem}}
        canvas{{width:100%!important;height:300px!important}}
        .pulse{{animation:pulse 2s infinite}}
        @keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.5}}}}
        .status{{display:inline-block;width:8px;height:8px;border-radius:50%;background:#10b981;margin-right:.5rem}}
        .status.offline{{background:#ef4444}}
        .recent{{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:16px;padding:1.5rem;margin-top:2rem}}
        table{{width:100%;border-collapse:collapse;font-size:.85rem}}
        th{{text-align:left;color:#9090a8;padding:.5rem 0;border-bottom:1px solid rgba(255,255,255,.1)}}
        td{{padding:.5rem 0;border-bottom:1px solid rgba(255,255,255,.04)}}
        .charts-grid{{display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;margin-bottom:2rem}}
        @media(max-width:768px){{.charts-grid{{grid-template-columns:1fr}}}}
        .brand{{font-size:.75rem;color:#666680;text-align:center;margin-top:2rem;padding-top:1rem;border-top:1px solid rgba(255,255,255,.05)}}
        .brand a{{color:#a855f7;text-decoration:none}}
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
</head>
<body>
<div class="container">
    <h1>📊 TrimTrack Analytics</h1>
    <p class="subtitle"><span class="status" id="wsStatus"></span>Short code: <strong>{short_code}</strong> | <span id="wsLabel">Connecting...</span></p>

    <div class="grid">
        <div class="card"><div class="card-label">Total Clicks</div><div class="card-value live" id="totalClicks">—</div></div>
        <div class="card"><div class="card-label">Unique Clicks</div><div class="card-value unique" id="uniqueClicks">—</div></div>
        <div class="card"><div class="card-label">Last Click</div><div class="card-value" id="lastClick" style="font-size:1rem">—</div></div>
    </div>

    <div class="charts-grid">
        <div class="chart-container"><div class="chart-title">⏱ Hourly Trend (24h)</div><canvas id="trendChart"></canvas></div>
        <div class="chart-container"><div class="chart-title">📅 Clicks Per Day (30d)</div><canvas id="dailyChart"></canvas></div>
    </div>
    <div class="recent"><div class="chart-title">🕐 Recent Clicks</div><table><thead><tr><th>Time</th><th>IP</th><th>User Agent</th></tr></thead><tbody id="recentTable"></tbody></table></div>
    <div class="brand">Powered by <a href="/">TrimTrack</a></div>
</div>

<script>
const SHORT_CODE = "{short_code}";
const API_BASE = window.location.origin;
let trendChart, dailyChart;

function initCharts() {{
    const baseOpts = {{ responsive: true, maintainAspectRatio: false, scales: {{ x: {{ ticks: {{ color: '#9090a8', maxRotation: 45, font: {{ size: 10 }} }}, grid: {{ color: 'rgba(255,255,255,0.05)' }} }}, y: {{ beginAtZero: true, ticks: {{ color: '#9090a8' }}, grid: {{ color: 'rgba(255,255,255,0.05)' }} }} }}, plugins: {{ legend: {{ display: false }} }} }};
    trendChart = new Chart(document.getElementById('trendChart').getContext('2d'), {{
        type: 'line',
        data: {{ labels: [], datasets: [{{ label: 'Clicks', data: [], borderColor: '#7c3aed', backgroundColor: 'rgba(124,58,237,0.1)', fill: true, tension: 0.4, pointRadius: 3 }}] }},
        options: baseOpts
    }});
    dailyChart = new Chart(document.getElementById('dailyChart').getContext('2d'), {{
        type: 'bar',
        data: {{ labels: [], datasets: [{{ label: 'Clicks', data: [], backgroundColor: 'rgba(168,85,247,0.6)', borderColor: '#a855f7', borderWidth: 1, borderRadius: 6 }}] }},
        options: baseOpts
    }});
}}

async function fetchAnalytics() {{
    try {{
        const res = await fetch(API_BASE + '/analytics/' + SHORT_CODE);
        const data = await res.json();
        document.getElementById('totalClicks').textContent = (data.total_clicks || 0).toLocaleString();
        document.getElementById('uniqueClicks').textContent = (data.unique_clicks || 0).toLocaleString();
        if (data.hourly_trend && data.hourly_trend.length) {{
            trendChart.data.labels = data.hourly_trend.map(h => new Date(h.hour).toLocaleTimeString([], {{hour:'2-digit',minute:'2-digit'}}));
            trendChart.data.datasets[0].data = data.hourly_trend.map(h => h.clicks);
            trendChart.update();
        }}
        if (data.daily_trend && data.daily_trend.length) {{
            dailyChart.data.labels = data.daily_trend.map(d => d.date);
            dailyChart.data.datasets[0].data = data.daily_trend.map(d => d.clicks);
            dailyChart.update();
        }}
        const recent = data.recent_clicks || [];
        document.getElementById('recentTable').innerHTML = recent.slice(0,10).map(c =>
            `<tr><td>${{new Date(c.clicked_at).toLocaleString()}}</td><td>${{c.ip_address||'—'}}</td><td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${{c.user_agent||'—'}}</td></tr>`
        ).join('');
        if (recent.length) document.getElementById('lastClick').textContent = new Date(recent[0].clicked_at).toLocaleString();
    }} catch(e) {{ console.error('Fetch error', e); }}
}}

function connectWS() {{
    const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
    const ws = new WebSocket(proto + '//' + location.host + '/ws/analytics/' + SHORT_CODE);
    ws.onopen = () => {{ document.getElementById('wsStatus').className = 'status'; document.getElementById('wsLabel').textContent = 'Live'; }};
    ws.onmessage = (e) => {{
        const data = JSON.parse(e.data);
        document.getElementById('totalClicks').textContent = data.total_clicks.toLocaleString();
        if (data.latest_click) {{
            document.getElementById('lastClick').textContent = new Date(data.latest_click.clicked_at).toLocaleString();
            fetchAnalytics();
        }}
    }};
    ws.onclose = () => {{ document.getElementById('wsStatus').className = 'status offline'; document.getElementById('wsLabel').textContent = 'Reconnecting...'; setTimeout(connectWS, 3000); }};
    ws.onerror = () => ws.close();
}}

initCharts();
fetchAnalytics();
connectWS();
setInterval(fetchAnalytics, 30000);
</script>
</body>
</html>"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.app_host, port=settings.app_port,
                reload=settings.debug, log_level="info")
