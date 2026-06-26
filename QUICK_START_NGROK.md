# 🚀 Quick Start: ngrok with URL Shortener

## What You Need To Do (5 minutes)

### Step 1: Install ngrok
Download from: https://ngrok.com/download

### Step 2: Get Your ngrok Public URL

**Terminal 1 - Start ngrok:**
```bash
ngrok http 8000
```

You'll see output like:
```
Forwarding    https://abcd-1234-5678.ngrok.io -> http://localhost:8000
```

**Copy the HTTPS URL** (e.g., `https://abcd-1234-5678.ngrok.io`)

### Step 3: Start Your App with ngrok URL

**Terminal 2 - Windows (PowerShell):**
```powershell
$env:NGROK_URL="https://abcd-1234-5678.ngrok.io"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Terminal 2 - Linux/macOS (Bash):**
```bash
export NGROK_URL="https://abcd-1234-5678.ngrok.io"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Step 4: Test on Mobile

1. **Create a short URL** (from your computer):
   ```bash
   curl -X POST http://localhost:8000/shorten \
     -H "Content-Type: application/json" \
     -d '{"url": "https://example.com"}'
   ```

2. **Response will show the public URL:**
   ```json
   {
     "short_url": "https://abcd-1234-5678.ngrok.io/abc123"
   }
   ```

3. **On your mobile phone:**
   - Open the short URL: `https://abcd-1234-5678.ngrok.io/abc123`
   - See the QR code
   - Scan with another phone's camera
   - **It should work! ✓**

## Using the Helper Script (Even Easier!)

**Windows:**
```powershell
.\run_with_ngrok.ps1
```

**Linux/macOS:**
```bash
chmod +x run_with_ngrok.sh
./run_with_ngrok.sh
```

This script automatically:
- ✓ Starts ngrok
- ✓ Gets the public URL
- ✓ Sets environment variable
- ✓ Starts your app

## What Changed in Your Code?

### 1. **New file: `app/utils/url_helpers.py`**
```python
def get_public_base_url() -> str:
    if settings.ngrok_url:
        return settings.ngrok_url
    return settings.base_url
```

### 2. **Updated: `app/config.py`**
- Added: `ngrok_url: Optional[str]` field
- Reads from `NGROK_URL` environment variable

### 3. **Updated: `app/routes/qr.py`**
- QR codes now use `get_public_base_url()`
- QR codes are scannable on mobile!

### 4. **Updated: `app/services/url_service.py`**
- Short URL responses use `get_public_base_url()`
- API returns the public ngrok URL

### 5. **Updated: `app/main.py`**
- Shows startup message with ngrok status:
  ```
  ✓ NGROK enabled! Public URL: https://abcd-1234-5678.ngrok.io
    QR codes will work on mobile phones with this URL
  ```

## How It Works

```
User scans QR on mobile
        ↓
Mobile browser opens: https://your-ngrok-url/abc123
        ↓
ngrok tunnel redirects to: http://localhost:8000/abc123
        ↓
Your app's redirect route sends user to original URL
        ↓
Mobile opens original website ✓
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| QR code doesn't work | Set `NGROK_URL` environment variable |
| "Connection refused" on mobile | Check ngrok tunnel is running |
| Different URL each time | Use paid ngrok plan for persistent domain |
| Port 8000 busy | Use different port: `ngrok http 9000` |

## Security Notes

⚠️ **Remember:**
- ngrok URLs are PUBLIC
- Anyone with the URL can access your app
- Don't expose sensitive data
- Use auth for sensitive endpoints
- Add `.env` to `.gitignore`

## Documentation Files

- **`NGROK_SETUP.md`** - Detailed setup guide with all options
- **`NGROK_IMPLEMENTATION.md`** - Technical implementation details
- **`run_with_ngrok.ps1`** - Windows helper script
- **`run_with_ngrok.sh`** - Linux/macOS helper script
- **`.env.example`** - Example configuration

## Next Steps

1. ✓ Install ngrok
2. ✓ Start ngrok tunnel
3. ✓ Set `NGROK_URL` and start app
4. ✓ Test on mobile
5. ✓ Enjoy!

---

**That's it! Your URL shortener now works on mobile phones! 🎉**

For more details, see `NGROK_SETUP.md` or `NGROK_IMPLEMENTATION.md`.
