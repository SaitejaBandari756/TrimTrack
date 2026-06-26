# NGROK Setup Guide for URL Shortener

This guide explains how to use ngrok to expose your local URL shortener as a public URL so QR codes work on mobile devices.

## What is ngrok?

ngrok is a reverse proxy that creates a secure public URL tunnel to your local server. It allows external devices (like mobile phones) to access your local development server.

## Installation

### Option 1: Using ngrok CLI

1. **Download ngrok**
   - Visit: https://ngrok.com/download
   - Download the latest version for your OS (Windows, macOS, Linux)
   - Extract the executable

2. **Add to PATH (Optional but recommended)**
   - Windows: Add ngrok.exe to your system PATH
   - macOS/Linux: Move ngrok to `/usr/local/bin`

3. **Verify Installation**
   ```bash
   ngrok version
   ```

### Option 2: Using pip (if available)
```bash
pip install pyngrok
```

## Running ngrok

### Basic Usage (Start ngrok tunnel)

1. **Start your application**
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

2. **In another terminal, start ngrok**
   ```bash
   ngrok http 8000
   ```

3. **Copy the public URL**
   - You'll see output like:
   ```
   ngrok                                                          (Ctrl+C to quit)
   
   Session Status                online
   Account                       your-email@example.com (Plan: Free)
   Version                       3.x.x
   Region                        us (United States)
   Latency                       45ms
   Web Interface                 http://127.0.0.1:4040
   Forwarding                    http://abcd-1234-5678.ngrok.io -> http://localhost:8000
   Forwarding                    https://abcd-1234-5678.ngrok.io -> http://localhost:8000
   ```
   - The public URLs are: `https://abcd-1234-5678.ngrok.io` (HTTPS is recommended)

## Configuration Methods

### Method 1: Environment Variable (Recommended)

Set the `NGROK_URL` environment variable before running your app:

**Windows (PowerShell):**
```powershell
$env:NGROK_URL="https://abcd-1234-5678.ngrok.io"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Windows (Command Prompt):**
```cmd
set NGROK_URL=https://abcd-1234-5678.ngrok.io
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**macOS/Linux (Bash):**
```bash
export NGROK_URL="https://abcd-1234-5678.ngrok.io"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Method 2: .env File

Create or update `.env` file in your project root:

```env
# Application
BASE_URL=http://localhost:8000
NGROK_URL=https://abcd-1234-5678.ngrok.io

# Database
DATABASE_URL=postgresql+asyncpg://urlshortener:urlshortener@localhost:5432/urlshortener

# Redis
REDIS_URL=redis://localhost:6379/0
```

## Complete Workflow

### Step 1: Start Your Application
```bash
# Windows (PowerShell)
$env:NGROK_URL="https://abcd-1234-5678.ngrok.io"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Linux/macOS
export NGROK_URL="https://abcd-1234-5678.ngrok.io"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Step 2: Start ngrok
In a separate terminal:
```bash
ngrok http 8000
```

### Step 3: Test Locally
```bash
# Create a short URL
curl -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# Response will include the ngrok public URL
# Example: "short_url": "https://abcd-1234-5678.ngrok.io/abc123"
```

### Step 4: Test on Mobile
1. Open the short URL in your mobile browser to see the QR code
2. Scan the QR code with another mobile phone
3. The ngrok public URL should work!

## Advanced Features

### Persistent URLs (Paid Plan)
By default, ngrok assigns a new URL each session. With a paid account, you can:
1. Reserve a fixed ngrok domain
2. Use it consistently without changing the `NGROK_URL` variable

```bash
ngrok http -subdomain=my-custom-domain 8000
# Public URL: https://my-custom-domain.ngrok.io
```

### Authentication
To protect your tunnel (recommended for production):
```bash
ngrok http -auth "user:password" 8000
```

### Custom Domain (Enterprise)
If you have a custom domain:
```env
NGROK_URL=https://my-app.example.com
```

## Troubleshooting

### Issue: "Connection refused" on mobile
**Solution:** Ensure `NGROK_URL` is set to the HTTPS URL from ngrok output

### Issue: QR code not scanning on mobile
**Solution:** 
- Verify the QR code URL matches your ngrok tunnel
- Use a QR code reader app to check the URL
- Ensure your mobile has internet connectivity

### Issue: ngrok tunnel keeps disconnecting
**Solution:**
- Free ngrok sessions timeout after 2 hours of inactivity
- Upgrade to a paid plan for persistent connections
- Keep terminal with ngrok running

### Issue: Port already in use
**Solution:** Change the port in both app and ngrok:
```bash
python -m uvicorn app.main:app --port 9000
ngrok http 9000
```

## URL Generation Flow

With ngrok configuration, here's how URLs are generated:

```
1. Request to POST /shorten
2. app/services/url_service.py creates short URL
3. Uses get_public_base_url() from app/utils/url_helpers.py
4. Returns: short_url = {NGROK_URL}/{short_code}
   Example: https://abcd-1234-5678.ngrok.io/abc123

5. QR Code Generation (GET /qr/{short_code})
6. Uses same get_public_base_url()
7. Generates QR code for: https://abcd-1234-5678.ngrok.io/abc123
8. Mobile scan → Redirects to long URL
```

## Security Considerations

⚠️ **Important:**
- Ngrok URLs are publicly accessible; anyone with the link can access your application
- Don't expose sensitive data through unprotected endpoints
- Use authentication for sensitive operations
- Never commit `.env` files with real ngrok URLs to version control
- Add `.env` to `.gitignore`

## Quick Start (Copy-Paste)

**Windows PowerShell:**
```powershell
$env:NGROK_URL="https://your-ngrok-url.ngrok.io"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
# In another terminal:
ngrok http 8000
```

**Linux/macOS:**
```bash
export NGROK_URL="https://your-ngrok-url.ngrok.io"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
# In another terminal:
ngrok http 8000
```

## Additional Resources

- ngrok Documentation: https://ngrok.com/docs
- FastAPI behind Proxy: https://fastapi.tiangolo.com/advanced/behind-a-proxy/
- QR Code Testing: Use your mobile camera or any QR app to scan

---

**Note:** Update the ngrok URL in the environment variable each time ngrok generates a new one (unless using a paid persistent domain).
