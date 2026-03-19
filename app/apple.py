import jwt
import time
from pathlib import Path
from django.conf import settings




def generate_apple_client_secret():
    key_value = settings.APPLE_PRIVATE_KEY

    # Detect if it's a file path or raw key
    if key_value.strip().startswith("-----BEGIN"):
        private_key = key_value  # Railway / ENV case
    else:
        private_key = Path(key_value).read_text() 
   
    payload = {
        "iss": settings.APPLE_TEAM_ID,
        "iat": int(time.time()),
        "exp": int(time.time()) + 86400 * 180,  # 6 months
        "aud": "https://appleid.apple.com",
        "sub": settings.APPLE_CLIENT_ID,
    }

    headers = {
        "kid": settings.APPLE_KEY_ID
    }

    token = jwt.encode(
        payload,
        private_key,
        algorithm="ES256",
        headers=headers
    )

    return token
