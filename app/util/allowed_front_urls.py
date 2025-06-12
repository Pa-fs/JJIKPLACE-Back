import os
from fastapi import Request
from dotenv import load_dotenv

load_dotenv()

ALLOWED_FRONTEND_URLS = os.getenv("ALLOWED_FRONTEND_URLS", "")
ALLOWED_FRONTEND_URLS = [url.strip() for url in ALLOWED_FRONTEND_URLS.split(",")]

def get_safe_redirect_url(request: Request):
    referer = request.headers.get("referer") or request.headers.get("origin")
    if referer:
        for allowed in ALLOWED_FRONTEND_URLS:
            if allowed in referer:
                return allowed  # 정확히 도메인만 반환

    return ALLOWED_FRONTEND_URLS[0]  # fallback