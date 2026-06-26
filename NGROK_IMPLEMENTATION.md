# ngrok Integration - Implementation Summary

## Overview
Your URL shortener application has been updated to support **ngrok** for exposing your local server as a public URL. This enables QR codes to work properly on mobile phones by using a publicly accessible URL instead of `localhost`.

## What Changed

### 1. **Configuration Updates** (`app/config.py`)
- Added `ngrok_url: Optional[str]` field to the `Settings` class
- This allows you to set an ngrok public URL via the `NGROK_URL` environment variable

### 2. **New URL Helper Utility** (`app/utils/url_helpers.py`)
Created a new utility module with two functions:
- `get_public_base_url()` - Returns the public URL (ngrok if configured, otherwise base_url)
- `is_using_ngrok()` - Checks if ngrok is currently being used

### 3. **QR Code Generation** (`app/routes/qr.py`)
- Updated to use `get_public_base_url()` instead of hardcoded `settings.base_url`
- QR codes now encode the public ngrok URL when configured
- Mobile phones can scan and access the shortened URLs

### 4. **URL Service** (`app/services/url_service.py`)
- Updated `create_short_url()` to use `get_public_base_url()`
- Short URL responses now include the public ngrok URL when configured
- API responses (JSON) show the correct public short URL

### 5. **Application Startup Logging** (`app/main.py`)
- Added import for URL helper utilities
- Enhanced startup logs to show:
  - Whether ngrok is enabled
  - The public URL being used
  - Instructions if ngrok is not configured

### 6. **Environment Configuration** (`.env.example`)
- Added `NGROK_URL` field with documentation
- Shows example of how to set ngrok URL

## How It Works

### URL Generation Flow
```
Request → POST /shorten
          ↓
       URL Service
          ↓
   get_public_base_url()
          ↓
   Check NGROK_URL env var
   ├─ If set → Use ngrok URL
   └─ If not → Use BASE_URL (localhost)
          ↓
   Response: {"short_url": "https://ngrok-url/abc123"}
```

### QR Code Flow
```
Request → GET /qr/{short_code}
          ↓
    get_public_base_url()
          ↓
   Generate QR code with public URL
          ↓
   Response: PNG image scannable on mobile
```

## Setup Instructions

### Quick Start (Windows PowerShell)

1. **Install ngrok** from https://ngrok.com/download

2. **Start ngrok tunnel**
   ```powershell
   ngrok http 8000
   ```
   Note the public URL (e.g., `https://abcd-1234-5678.ngrok.io`)

3. **In another terminal, set environment variable and start app**
   ```powershell
   $env:NGROK_URL="https://abcd-1234-5678.ngrok.io"
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

4. **Test on mobile**
   - Create a short URL from your app
   - Scan the QR code with a mobile phone
   - It should work!

### Using the Helper Script (Recommended)

**Windows:**
```powershell
.\run_with_ngrok.ps1
```
This automatically:
- Checks ngrok installation
- Activates virtual environment
- Starts ngrok tunnel
- Retrieves the public URL
- Sets environment variable
- Starts the FastAPI app

**Linux/macOS:**
```bash
chmod +x run_with_ngrok.sh
./run_with_ngrok.sh
```
Same features as PowerShell version

### Using .env File

Create/update `.env`:
```env
NGROK_URL=https://abcd-1234-5678.ngrok.io
```

Then start the app normally:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Files Modified
- `app/config.py` - Added ngrok_url field
- `app/routes/qr.py` - Uses public base URL
- `app/services/url_service.py` - Uses public base URL in responses
- `app/main.py` - Enhanced logging
- `.env.example` - Added NGROK_URL example

## Files Added
- `app/utils/url_helpers.py` - URL resolution utility
- `NGROK_SETUP.md` - Detailed setup guide
- `run_with_ngrok.ps1` - Windows helper script
- `run_with_ngrok.sh` - Linux/macOS helper script

## Environment Variables

### Required (when using ngrok)
- `NGROK_URL` - Your ngrok public URL (e.g., `https://abcd-1234-5678.ngrok.io`)

### Optional
- `BASE_URL` - Local base URL (default: `http://localhost:8000`)
- `DEBUG` - Debug mode (default: `false`)

## Example Workflow

```bash
# Terminal 1: Start ngrok
ngrok http 8000
# Output: Forwarding ... https://abcd-1234-5678.ngrok.io

# Terminal 2: Set env var and start app
export NGROK_URL="https://abcd-1234-5678.ngrok.io"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# App logs will show:
# ✓ NGROK enabled! Public URL: https://abcd-1234-5678.ngrok.io
# QR codes will work on mobile phones with this URL

# Terminal 3: Test API (from another machine or mobile)
curl https://abcd-1234-5678.ngrok.io/shorten \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# Response:
# {
#   "short_url": "https://abcd-1234-5678.ngrok.io/abc123",
#   ...
# }

# Scan the QR code on mobile → Opens the shortened URL!
```

## Testing

### Local Testing
```bash
curl -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

### Mobile Testing
1. Create short URL using the API
2. Access the short URL in browser: `https://your-ngrok-url/abc123`
3. Use mobile QR code scanner on the generated QR code
4. Should redirect to original URL

## Troubleshooting

**Issue**: QR code doesn't work on mobile
- **Solution**: Verify `NGROK_URL` is set correctly in environment
- Check app startup logs show ngrok is enabled
- Ensure mobile has internet connectivity

**Issue**: "Connection refused" on mobile
- **Solution**: Make sure ngrok tunnel is running
- Use HTTPS URL from ngrok output

**Issue**: Port 8000 already in use
- **Solution**: Change port: `python -m uvicorn app.main:app --port 9000`
- Also update ngrok: `ngrok http 9000`

## Security Notes

⚠️ **Important**:
- Ngrok URLs are publicly accessible
- Anyone with the URL can access your app
- Don't expose sensitive endpoints without auth
- Add `.env` to `.gitignore` (never commit real ngrok URLs)
- Use authentication for sensitive operations
- Consider ngrok authentication for production

## Next Steps

1. Read `NGROK_SETUP.md` for detailed instructions
2. Install ngrok from https://ngrok.com/download
3. Use `run_with_ngrok.ps1` (Windows) or `run_with_ngrok.sh` (Linux/macOS)
4. Test QR code scanning on mobile phone
5. Enjoy mobile-accessible short URLs!

## Support

For more information:
- ngrok docs: https://ngrok.com/docs
- FastAPI docs: https://fastapi.tiangolo.com
- QR Code scanning: Use mobile camera or any QR app

---

**Note**: Each ngrok session generates a new URL (unless using paid plan). Update `NGROK_URL` environment variable whenever you restart ngrok.
