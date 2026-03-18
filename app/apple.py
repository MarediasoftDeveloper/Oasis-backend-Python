import jwt
import time
from pathlib import Path
from django.conf import settings


def get_apple_private_key():
    key = settings.APPLE_PRIVATE_KEY
    
    if Path(key).exists():
        return Path(key).read_text()
    print(key)
    return key

def generate_apple_client_secret():
    private_key = get_apple_private_key()
    
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
