"""Read credentials without copying, executing, or printing them."""
import os
from pathlib import Path
from urllib.parse import urlparse
from dotenv import dotenv_values
ROOT = Path(__file__).resolve().parents[2]

def credentials():
    values = dotenv_values(ROOT / 'credentials' / 'nebius.env')
    key = os.environ.get('NEBIUS_API_KEY') or values.get('NEBIUS_API_KEY')
    base = os.environ.get('NEBIUS_BASE_URL') or values.get('NEBIUS_BASE_URL') or 'https://api.tokenfactory.nebius.com/v1/'
    parsed = urlparse(base)
    if parsed.scheme != 'https' or not (parsed.hostname or '').endswith('.nebius.com') or parsed.username:
        raise ValueError('Refusing to send credentials to an unverified endpoint')
    if not key or key.startswith('PASTE'):
        raise ValueError('Nebius credential unavailable')
    return base.rstrip('/') + '/', key
