import os
os.environ['NGROK_URL'] = 'https://0f31-2405-201-c03e-e8c5-ad46-a663-cf34-f828.ngrok-free.app'

from app.config import settings
from app.utils.url_helpers import get_public_base_url

print(f"✓ Settings ngrok_url: {settings.ngrok_url}")
print(f"✓ get_public_base_url(): {get_public_base_url()}")
print(f"✓ Generated short URL: {get_public_base_url()}/testcode123")
