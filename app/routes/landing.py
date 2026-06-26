from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse, tags=["Landing"], include_in_schema=False)
async def landing_page():
    return HTMLResponse(content=_get_landing_html())


def _get_landing_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TrimTrack — Smart URL Shortener</title>
    <meta name="description" content="TrimTrack — Production-grade URL shortener with click analytics, QR code generation, and advanced threat detection.">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
    <style>
        *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

        :root {
            --bg-primary: #0a0e27;
            --bg-card: rgba(255, 255, 255, 0.05);
            --bg-glass: rgba(255, 255, 255, 0.02);
            --border: rgba(255, 255, 255, 0.08);
            --border-hover: rgba(139, 92, 246, 0.4);
            --text-primary: #f0f0f5;
            --text-secondary: #9090a8;
            --text-muted: #666680;
            --accent-1: #7c3aed;
            --accent-2: #a855f7;
            --accent-3: #d946ef;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --radius: 20px;
        }

        body {
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, var(--bg-primary) 0%, #1a1f3a 100%);
            color: var(--text-primary);
            min-height: 100vh;
            overflow-x: hidden;
            position: relative;
        }

        .bg-orb {
            position: fixed;
            border-radius: 50%;
            filter: blur(120px);
            opacity: 0.1;
            pointer-events: none;
            z-index: 0;
        }
        .bg-orb-1 {
            width: 800px; height: 800px;
            background: var(--accent-1);
            top: -200px; left: -200px;
            animation: float-orb 25s ease-in-out infinite;
        }
        .bg-orb-2 {
            width: 600px; height: 600px;
            background: var(--accent-2);
            bottom: -100px; right: -100px;
            animation: float-orb 30s ease-in-out infinite reverse;
        }
        .bg-orb-3 {
            width: 500px; height: 500px;
            background: var(--accent-3);
            top: 40%; left: 50%;
            transform: translate(-50%, -50%);
            animation: float-orb 20s ease-in-out infinite 2s;
        }
        @keyframes float-orb {
            0%, 100% { transform: translate(0, 0) scale(1); }
            25% { transform: translate(50px, -60px) scale(1.05); }
            50% { transform: translate(-30px, 50px) scale(0.95); }
            75% { transform: translate(60px, 30px) scale(1.03); }
        }

        body::before {
            content: '';
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
            pointer-events: none;
            z-index: 1;
        }

        .container {
            position: relative;
            z-index: 2;
            max-width: 900px;
            margin: 0 auto;
            padding: 60px 20px;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }

        .header {
            text-align: center;
            margin-bottom: 50px;
        }

        .logo-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            background: var(--bg-glass);
            border: 1px solid var(--border);
            border-radius: 50px;
            margin-bottom: 20px;
            font-size: 13px;
            color: var(--text-secondary);
            backdrop-filter: blur(10px);
        }

        .logo-badge span {
            width: 8px;
            height: 8px;
            background: var(--success);
            border-radius: 50%;
            animation: pulse 2s ease-in-out infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }

        .title {
            font-size: 56px;
            font-weight: 800;
            margin-bottom: 20px;
            background: linear-gradient(135deg, var(--accent-2), var(--accent-1), var(--accent-3));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: -1px;
        }

        .subtitle {
            font-size: 18px;
            color: var(--text-secondary);
            margin-bottom: 40px;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
            line-height: 1.6;
        }

        .card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 40px;
            backdrop-filter: blur(20px);
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            width: 100%;
        }

        .input-group {
            position: relative;
            margin-bottom: 25px;
        }

        .input-label {
            display: block;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 10px;
            color: var(--text-primary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .input-field {
            width: 100%;
            padding: 14px 16px;
            background: rgba(255, 255, 255, 0.06);
            border: 1.5px solid var(--border);
            border-radius: 12px;
            color: var(--text-primary);
            font-size: 16px;
            font-family: 'Space Mono', monospace;
            transition: all 0.3s ease;
        }

        .input-field:focus {
            outline: none;
            border-color: var(--border-hover);
            background: rgba(139, 92, 246, 0.08);
            box-shadow: 0 0 20px rgba(139, 92, 246, 0.2);
        }

        .input-field::placeholder {
            color: var(--text-muted);
        }

        .analysis-box {
            background: rgba(139, 92, 246, 0.05);
            border: 1px solid rgba(139, 92, 246, 0.2);
            border-radius: 12px;
            padding: 15px;
            margin-top: 12px;
            display: none;
            font-size: 13px;
            color: var(--text-secondary);
        }

        .analysis-box.show {
            display: block;
            animation: slideIn 0.3s ease-out;
        }

        @keyframes slideIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .analysis-item {
            display: flex;
            align-items: center;
            gap: 8px;
            margin: 8px 0;
        }

        .analysis-icon {
            font-size: 16px;
            min-width: 20px;
        }

        .analysis-item.safe .analysis-icon { color: var(--success); }
        .analysis-item.warning .analysis-icon { color: var(--warning); }
        .analysis-item.danger .analysis-icon { color: var(--danger); }

        .safety-score {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 20px;
            padding: 12px;
            background: rgba(16, 185, 129, 0.05);
            border-radius: 10px;
            border: 1px solid rgba(16, 185, 129, 0.2);
            display: none;
        }

        .safety-score.show {
            display: flex;
        }

        .safety-score.warn {
            background: rgba(245, 158, 11, 0.05);
            border-color: rgba(245, 158, 11, 0.2);
        }

        .safety-score.danger {
            background: rgba(239, 68, 68, 0.05);
            border-color: rgba(239, 68, 68, 0.2);
        }

        .score-bar {
            flex: 1;
            height: 8px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
            overflow: hidden;
        }

        .score-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--success), var(--accent-2));
            border-radius: 4px;
            transition: width 0.5s ease;
        }

        .score-fill.warn {
            background: linear-gradient(90deg, var(--warning), var(--accent-3));
        }

        .score-fill.danger {
            background: linear-gradient(90deg, var(--danger), #8b0000);
        }

        .score-text {
            font-size: 12px;
            font-weight: 600;
            color: var(--text-secondary);
            min-width: 50px;
        }

        .button-group {
            display: flex;
            gap: 12px;
            margin-top: 25px;
        }

        .button {
            flex: 1;
            padding: 14px 24px;
            border: none;
            border-radius: 12px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .button-primary {
            background: linear-gradient(135deg, var(--accent-1), var(--accent-2));
            color: white;
            box-shadow: 0 10px 30px rgba(124, 58, 237, 0.3);
        }

        .button-primary:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 15px 40px rgba(124, 58, 237, 0.4);
        }

        .button-primary:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .button-secondary {
            background: var(--bg-glass);
            border: 1.5px solid var(--border);
            color: var(--text-primary);
        }

        .button-secondary:hover {
            border-color: var(--border-hover);
            background: rgba(139, 92, 246, 0.1);
        }

        .result-section {
            margin-top: 30px;
            padding-top: 30px;
            border-top: 1px solid var(--border);
            display: none;
        }

        .result-section.show {
            display: block;
            animation: slideIn 0.3s ease-out;
        }

        .result-label {
            font-size: 12px;
            font-weight: 600;
            color: var(--text-muted);
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .result-box {
            background: rgba(139, 92, 246, 0.08);
            border: 1.5px solid rgba(139, 92, 246, 0.3);
            border-radius: 12px;
            padding: 16px;
            word-break: break-all;
            font-family: 'Space Mono', monospace;
            font-size: 14px;
            color: var(--accent-2);
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .result-actions {
            display: flex;
            gap: 10px;
            margin-top: 16px;
            flex-wrap: wrap;
        }

        .action-btn {
            padding: 10px 18px;
            border: 1.5px solid var(--border);
            background: var(--bg-glass);
            color: var(--text-primary);
            border-radius: 10px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
            display: inline-flex;
            align-items: center;
            gap: 6px;
            text-decoration: none;
        }

        .action-btn:hover {
            border-color: var(--border-hover);
            background: rgba(139, 92, 246, 0.1);
            transform: translateY(-1px);
        }

        .action-btn.primary {
            background: linear-gradient(135deg, var(--accent-1), var(--accent-2));
            border-color: transparent;
            color: white;
        }

        .action-btn.primary:hover {
            box-shadow: 0 8px 24px rgba(124, 58, 237, 0.4);
        }

        .copy-btn {
            background: rgba(255, 255, 255, 0.1);
            border: none;
            color: var(--text-primary);
            padding: 8px 12px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 600;
            transition: all 0.2s ease;
        }

        .copy-btn:hover {
            background: rgba(255, 255, 255, 0.2);
        }

        .copy-btn.copied {
            background: var(--success);
            color: white;
        }

        /* QR Code Section */
        .qr-section {
            margin-top: 20px;
            display: none;
        }

        .qr-section.show {
            display: block;
            animation: slideIn 0.4s ease-out;
        }

        .qr-card {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 24px;
            display: flex;
            align-items: center;
            gap: 24px;
            backdrop-filter: blur(10px);
        }

        .qr-image-wrapper {
            flex-shrink: 0;
            width: 150px;
            height: 150px;
            background: white;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 8px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }

        .qr-image-wrapper img {
            width: 100%;
            height: 100%;
            object-fit: contain;
        }

        .qr-info {
            flex: 1;
        }

        .qr-title {
            font-size: 16px;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .qr-desc {
            font-size: 13px;
            color: var(--text-secondary);
            margin-bottom: 16px;
            line-height: 1.5;
        }

        .qr-loading {
            display: flex;
            align-items: center;
            gap: 10px;
            color: var(--text-muted);
            font-size: 13px;
        }

        @media (max-width: 600px) {
            .qr-card {
                flex-direction: column;
                text-align: center;
            }
        }

        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.7);
            backdrop-filter: blur(4px);
            animation: fadeIn 0.3s ease;
        }

        .modal.show {
            display: flex;
            align-items: center;
            justify-content: center;
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        .modal-content {
            background: linear-gradient(135deg, rgba(10, 14, 39, 0.95), rgba(26, 31, 58, 0.95));
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 40px;
            max-width: 500px;
            width: 90%;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
            animation: slideInCenter 0.3s ease-out;
            backdrop-filter: blur(20px);
        }

        @keyframes slideInCenter {
            from { opacity: 0; transform: scale(0.9) translateY(-20px); }
            to { opacity: 1; transform: scale(1) translateY(0); }
        }

        .modal-header {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 20px;
        }

        .modal-icon {
            font-size: 40px;
        }

        .modal-title {
            font-size: 24px;
            font-weight: 700;
            color: var(--text-primary);
        }

        .modal-message {
            color: var(--text-secondary);
            margin-bottom: 25px;
            line-height: 1.6;
        }

        .modal-footer {
            display: flex;
            gap: 12px;
            margin-top: 30px;
        }

        .modal-footer button {
            flex: 1;
            padding: 12px;
            border: none;
            border-radius: 10px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            text-transform: uppercase;
            font-size: 13px;
            letter-spacing: 0.5px;
        }

        .modal-cancel {
            background: var(--bg-glass);
            border: 1.5px solid var(--border);
            color: var(--text-primary);
        }

        .modal-cancel:hover {
            background: rgba(255, 255, 255, 0.08);
        }

        .modal-confirm {
            background: linear-gradient(135deg, var(--accent-1), var(--accent-2));
            color: white;
        }

        .modal-confirm:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(124, 58, 237, 0.3);
        }

        .modal-confirm.danger {
            background: linear-gradient(135deg, var(--danger), #b91c1c);
        }

        .spinner {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid rgba(255, 255, 255, 0.2);
            border-top: 2px solid var(--accent-2);
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 20px;
            margin-top: 50px;
            padding-top: 50px;
            border-top: 1px solid var(--border);
            width: 100%;
        }

        .feature-card {
            background: var(--bg-glass);
            border: 1px solid var(--border);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }

        .feature-card:hover {
            border-color: var(--border-hover);
            transform: translateY(-5px);
        }

        .feature-icon {
            font-size: 32px;
            margin-bottom: 12px;
        }

        .feature-title {
            font-size: 14px;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 8px;
        }

        .feature-desc {
            font-size: 12px;
            color: var(--text-muted);
        }

        @media (max-width: 768px) {
            .title {
                font-size: 36px;
            }

            .subtitle {
                font-size: 16px;
            }

            .card {
                padding: 30px 20px;
            }

            .container {
                padding: 30px 16px;
            }

            .features-grid {
                grid-template-columns: 1fr 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="bg-orb bg-orb-1"></div>
    <div class="bg-orb bg-orb-2"></div>
    <div class="bg-orb bg-orb-3"></div>

    <div class="container">
        <div class="header">
            <div class="logo-badge">
                <span></span>
                ✂️ Smart Link Shortener
            </div>
            <h1 class="title">TrimTrack</h1>
            <p class="subtitle">Shorten, track, and analyze your links with QR code generation, unique click tracking, and real-time analytics</p>
        </div>

        <div class="card">
            <div class="safety-score" id="safetyScore">
                <div class="score-bar">
                    <div class="score-fill" id="scoreFill"></div>
                </div>
                <span class="score-text" id="scoreText">100%</span>
            </div>

            <div class="input-group">
                <label class="input-label">📎 Original URL</label>
                <div class="input-wrapper">
                    <input type="text" id="urlInput" class="input-field" placeholder="https://example.com/very-long-url-here">
                </div>
                <div class="analysis-box" id="analysisBox"></div>
            </div>

            <div class="button-group">
                <button class="button button-primary" id="shortenBtn" onclick="shortenURL()">
                    <span id="btnText">🚀 Generate Short Link</span>
                </button>
                <button class="button button-secondary" id="clearBtn" onclick="clearForm()">Clear</button>
            </div>

            <div class="result-section" id="resultSection">
                <div class="result-label">✨ Your Short Link</div>
                <div class="result-box">
                    <span id="shortUrlDisplay"></span>
                    <button class="copy-btn" id="copyBtn" onclick="copyShortUrl()">Copy</button>
                </div>
                <div class="result-actions">
                    <button class="action-btn primary" id="copyLinkBtn" onclick="copyShortUrl()">📋 Copy Link</button>
                    <a class="action-btn" id="dashboardLink" href="#" target="_blank">📊 Analytics</a>
                    <button class="action-btn" id="downloadQrBtn" onclick="downloadQR()" style="display:none">⬇️ Download QR</button>
                </div>

                <div class="qr-section" id="qrSection">
                    <div class="qr-card">
                        <div class="qr-image-wrapper">
                            <img id="qrImage" src="" alt="QR Code">
                        </div>
                        <div class="qr-info">
                            <div class="qr-title">📱 QR Code Ready</div>
                            <div class="qr-desc">Scan this QR code with any mobile device to open your shortened link. Perfect for sharing on print, presentations, or social media.</div>
                            <button class="action-btn primary" onclick="downloadQR()">⬇️ Download PNG</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="features-grid">
            <div class="feature-card">
                <div class="feature-icon">📱</div>
                <div class="feature-title">QR Codes</div>
                <div class="feature-desc">Auto-generated QR for every link</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <div class="feature-title">Click Analytics</div>
                <div class="feature-desc">Unique visitors, daily trends & more</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🔍</div>
                <div class="feature-title">Link Analysis</div>
                <div class="feature-desc">Real-time malware & threat scanning</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">⚡</div>
                <div class="feature-title">Lightning Fast</div>
                <div class="feature-desc">Sub-millisecond redirects</div>
            </div>
        </div>
    </div>

    <div class="modal" id="warningModal">
        <div class="modal-content">
            <div class="modal-header" id="modalHeader"></div>
            <div class="modal-message" id="modalMessage"></div>
            <div class="modal-footer">
                <button class="modal-cancel" onclick="closeWarning()">Cancel</button>
                <button class="modal-confirm" id="modalConfirm" onclick="confirmWarning()">Continue Anyway</button>
            </div>
        </div>
    </div>

    <!-- Toast Notification Overlay -->
    <div id="toastOverlay" style="display:none;position:fixed;z-index:2000;left:0;top:0;width:100%;height:100%;background:rgba(0,0,0,0.5);backdrop-filter:blur(6px);transition:opacity .3s ease;opacity:0;justify-content:center;align-items:center;">
        <div id="toastCard" style="background:linear-gradient(135deg,rgba(10,14,39,0.97),rgba(26,31,58,0.97));border:1px solid rgba(255,255,255,0.1);border-radius:20px;padding:36px 40px;max-width:460px;width:90%;box-shadow:0 24px 80px rgba(0,0,0,0.6),0 0 40px rgba(124,58,237,0.15);transform:scale(0.9) translateY(20px);transition:transform .35s cubic-bezier(.34,1.56,.64,1),opacity .3s ease;opacity:0;text-align:center;">
            <div id="toastIcon" style="font-size:48px;margin-bottom:16px;"></div>
            <div id="toastTitle" style="font-size:20px;font-weight:700;color:#f0f0f5;margin-bottom:10px;"></div>
            <div id="toastMessage" style="font-size:14px;color:#9090a8;line-height:1.6;margin-bottom:28px;"></div>
            <button onclick="hideToast()" style="padding:12px 36px;border:none;border-radius:12px;background:linear-gradient(135deg,#7c3aed,#a855f7);color:white;font-size:14px;font-weight:600;cursor:pointer;transition:all .2s ease;text-transform:uppercase;letter-spacing:0.5px;">Got it</button>
        </div>
    </div>

    <script>
        const urlInput = document.getElementById('urlInput');
        const analysisBox = document.getElementById('analysisBox');
        const safetyScore = document.getElementById('safetyScore');
        const shortenBtn = document.getElementById('shortenBtn');
        const resultSection = document.getElementById('resultSection');
        const shortUrlDisplay = document.getElementById('shortUrlDisplay');
        const warningModal = document.getElementById('warningModal');
        const modalHeader = document.getElementById('modalHeader');
        const modalMessage = document.getElementById('modalMessage');
        const modalConfirm = document.getElementById('modalConfirm');

        let currentUrl = '';
        let currentResponse = null;
        let currentShortCode = '';
        let pendingWarning = false;

        /* ━━━ Toast Notification System ━━━ */
        function showToast(title, message, type = 'error') {
            const overlay = document.getElementById('toastOverlay');
            const card = document.getElementById('toastCard');
            const iconEl = document.getElementById('toastIcon');
            const titleEl = document.getElementById('toastTitle');
            const msgEl = document.getElementById('toastMessage');

            const icons = { error: '⚠️', success: '✅', info: 'ℹ️', warning: '🚨' };
            const borderColors = {
                error: 'rgba(239,68,68,0.4)',
                success: 'rgba(16,185,129,0.4)',
                info: 'rgba(124,58,237,0.4)',
                warning: 'rgba(245,158,11,0.4)'
            };

            iconEl.textContent = icons[type] || icons.error;
            titleEl.textContent = title;
            msgEl.textContent = message;
            card.style.borderColor = borderColors[type] || borderColors.error;

            overlay.style.display = 'flex';
            requestAnimationFrame(() => {
                overlay.style.opacity = '1';
                card.style.opacity = '1';
                card.style.transform = 'scale(1) translateY(0)';
            });

            overlay.onclick = (e) => { if (e.target === overlay) hideToast(); };
        }

        function hideToast() {
            const overlay = document.getElementById('toastOverlay');
            const card = document.getElementById('toastCard');
            overlay.style.opacity = '0';
            card.style.opacity = '0';
            card.style.transform = 'scale(0.9) translateY(20px)';
            setTimeout(() => { overlay.style.display = 'none'; }, 300);
        }

        /* ━━━ Safety Score Display ━━━ */
        function updateSafetyScore(score) {
            const percentage = Math.round(score * 100);
            safetyScore.classList.add('show');

            let className = 'safe';
            if (percentage < 30) className = 'danger';
            else if (percentage < 70) className = 'warn';

            document.getElementById('scoreFill').className = 'score-fill ' + className;
            document.getElementById('scoreFill').style.width = percentage + '%';
            document.getElementById('scoreText').textContent = percentage + '%';

            safetyScore.className = 'safety-score show ' + className;
        }

        /* ━━━ Shorten URL ━━━ */
        async function shortenURL() {
            const url = urlInput.value.trim();
            if (!url) {
                showToast('Missing URL', 'Please enter a URL to shorten.', 'warning');
                return;
            }

            if (!url.startsWith('http://') && !url.startsWith('https://')) {
                showToast('Invalid URL', 'URL must start with http:// or https://', 'error');
                return;
            }

            shortenBtn.disabled = true;
            shortenBtn.innerHTML = '<span class="spinner"></span>';

            try {
                const response = await fetch('/shorten', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url })
                });

                const data = await response.json();

                if (response.ok) {
                    currentUrl = url;
                    currentResponse = data;

                    // Show safety score
                    updateSafetyScore(data.safety_score);

                    if (data.has_warnings && data.warnings && data.warnings.warning_type) {
                        showWarning(data.warnings);
                    } else {
                        displayResult(data);
                    }
                } else if (response.status === 429) {
                    showToast('Rate Limit Reached', 'Too many URL creation requests. Please wait a minute and try again.', 'warning');
                } else {
                    if (data.warnings && data.warnings.warning_type === 'ADULT_CONTENT') {
                        showWarning(data.warnings);
                    } else {
                        showToast('Error', data.detail || 'Something went wrong. Please try again.', 'error');
                    }
                }
            } catch (e) {
                showToast('Connection Error', 'Could not connect to the server. Please check your connection.', 'error');
            } finally {
                shortenBtn.disabled = false;
                shortenBtn.innerHTML = '🚀 Generate Short Link';
            }
        }

        /* ━━━ Safety Warning Modal ━━━ */
        function showWarning(warning) {
            const warningTypes = {
                'ADULT_CONTENT': {
                    icon: '🚫',
                    title: 'Adult Content Detected',
                    message: 'This URL leads to adult/NSFW content. This is blocked by TrimTrack for security and compliance reasons.',
                    isDanger: true
                },
                'MALWARE': {
                    icon: '⚠️',
                    title: 'Malware Risk Detected',
                    message: 'This URL may contain malware, including APK files or suspicious downloads. Proceed with caution.',
                    isDanger: true
                },
                'MALICIOUS_PATTERN': {
                    icon: '🚨',
                    title: 'Suspicious Pattern Found',
                    message: 'This URL matches known malicious patterns. It may be phishing or exploit attempt.',
                    isDanger: true
                },
                'BLOCKED_DOMAIN': {
                    icon: '🔒',
                    title: 'Blocked Domain',
                    message: 'This domain is on our security blocklist.',
                    isDanger: true
                },
                'SUSPICIOUS': {
                    icon: '⚠️',
                    title: 'Suspicious Activity',
                    message: warning.message,
                    isDanger: true
                }
            };

            const type = warningTypes[warning.warning_type] || warningTypes['SUSPICIOUS'];

            modalHeader.innerHTML = `<span class="modal-icon">${type.icon}</span><span class="modal-title">${type.title}</span>`;
            modalMessage.textContent = type.message;

            if (type.isDanger) {
                modalConfirm.textContent = '⚠️ Accept Anyway';
                modalConfirm.classList.add('danger');
            }

            pendingWarning = true;
            warningModal.classList.add('show');
        }

        function closeWarning() {
            warningModal.classList.remove('show');
            pendingWarning = false;
            currentResponse = null;
        }

        function confirmWarning() {
            warningModal.classList.remove('show');
            pendingWarning = false;
            if (currentResponse) {
                displayResult(currentResponse);
            }
        }

        /* ━━━ Display Result ━━━ */
        function displayResult(data) {
            currentShortCode = data.short_code;
            shortUrlDisplay.textContent = data.short_url;
            resultSection.classList.add('show');
            document.getElementById('copyBtn').textContent = 'Copy';
            document.getElementById('copyBtn').classList.remove('copied');

            // Set dashboard link
            const dashLink = document.getElementById('dashboardLink');
            dashLink.href = '/dashboard/' + data.short_code;

            // Load QR code
            loadQRCode(data.short_code);
        }

        async function loadQRCode(shortCode) {
            const qrSection = document.getElementById('qrSection');
            const qrImage = document.getElementById('qrImage');
            const downloadBtn = document.getElementById('downloadQrBtn');

            try {
                const response = await fetch('/qr/' + shortCode);
                if (response.ok) {
                    const blob = await response.blob();
                    const url = URL.createObjectURL(blob);
                    qrImage.src = url;
                    qrSection.classList.add('show');
                    downloadBtn.style.display = 'inline-flex';
                }
            } catch (e) {
                console.error('QR load error:', e);
            }
        }

        function downloadQR() {
            const qrImage = document.getElementById('qrImage');
            if (!qrImage.src) return;

            const a = document.createElement('a');
            a.href = qrImage.src;
            a.download = 'trimtrack-qr-' + currentShortCode + '.png';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        }

        function copyShortUrl() {
            const url = shortUrlDisplay.textContent;
            navigator.clipboard.writeText(url).then(() => {
                const btn = document.getElementById('copyBtn');
                btn.textContent = '✓ Copied!';
                btn.classList.add('copied');
                const linkBtn = document.getElementById('copyLinkBtn');
                linkBtn.innerHTML = '✅ Copied!';
                setTimeout(() => {
                    btn.textContent = 'Copy';
                    btn.classList.remove('copied');
                    linkBtn.innerHTML = '📋 Copy Link';
                }, 2000);
            });
        }

        function clearForm() {
            urlInput.value = '';
            analysisBox.classList.remove('show');
            safetyScore.classList.remove('show');
            resultSection.classList.remove('show');
            document.getElementById('qrSection').classList.remove('show');
            document.getElementById('downloadQrBtn').style.display = 'none';
        }

        urlInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') shortenURL();
        });
    </script>
</body>
</html>"""
