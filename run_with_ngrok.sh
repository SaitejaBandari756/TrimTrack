echo "╔════════════════════════════════════════════════════════════╗"
echo "║  URL Shortener with ngrok - Mobile QR Code Setup          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

echo "Checking for ngrok..."
if ! command -v ngrok &> /dev/null; then
    echo "✗ ngrok not found! Please install ngrok from https://ngrok.com/download"
    echo ""
    echo "Installation options:"
    echo "  macOS (homebrew):  brew install ngrok/ngrok/ngrok"
    echo "  Manual:            Download from https://ngrok.com/download"
    exit 1
fi
NGROK_PATH=$(command -v ngrok)
echo "✓ ngrok found at: $NGROK_PATH"

echo ""
echo "Activating Python virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "✗ Failed to activate virtual environment"
    exit 1
fi
echo "✓ Virtual environment activated"

echo ""
echo "Starting ngrok tunnel (port 8000)..."
ngrok http 8000 &
NGROK_PID=$!
echo "✓ ngrok tunnel starting (PID: $NGROK_PID)..."
echo ""
echo "⏳ Waiting for ngrok to initialize (5 seconds)..."
sleep 5

echo ""
echo "Retrieving public ngrok URL..."
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url')

if [ ! -z "$NGROK_URL" ] && [ "$NGROK_URL" != "null" ]; then
    echo "✓ ngrok public URL: $NGROK_URL"
    echo ""
    echo "Setting NGROK_URL environment variable..."
    export NGROK_URL=$NGROK_URL
    echo "✓ NGROK_URL=$NGROK_URL"
else
    echo "⚠ Could not retrieve ngrok URL automatically"
    echo "Please check ngrok tunnel at http://localhost:4040"
    echo ""
    echo "Once you have the URL, you can set it manually:"
    echo "  export NGROK_URL='https://your-ngrok-url.ngrok.io'"
fi

echo ""
echo "Starting FastAPI application (port 8000)..."
echo "════════════════════════════════════════════════════════════"
echo ""

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

echo ""
echo "════════════════════════════════════════════════════════════"
echo "Application stopped. ngrok tunnel is still running."
echo "Access ngrok dashboard: http://localhost:4040"
echo ""

echo "Killing ngrok process (PID: $NGROK_PID)..."
kill $NGROK_PID 2>/dev/null || true
echo "Done!"
