import re

with open('server/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add SecurityHeadersMiddleware and slowapi exception handler
middleware_code = """
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
import slowapi

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://api.github.com https://gmail.googleapis.com"
        )
        return response

app.add_middleware(SecurityHeadersMiddleware)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
"""

# Replace exception handler to not leak stack trace
# Find the global exception handler
old_handler = """    logging.getLogger("workspace").exception("Unhandled exception:")
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error", 
            "detail": str(exc),
            "traceback": traceback.format_exc()
        }
    )"""

new_handler = """    logging.getLogger("workspace").exception("Unhandled exception:")
    return JSONResponse(
        status_code=500,
        content={"error": "internal_server_error"}
    )"""

content = content.replace(old_handler, new_handler)

if "SecurityHeadersMiddleware" not in content:
    # Insert after CORSMiddleware
    content = content.replace("app.add_middleware(\n    CORSMiddleware, allow_origins=list(_origins),\n    allow_credentials=True, allow_methods=[\"*\"], allow_headers=[\"*\"],\n)", "app.add_middleware(\n    CORSMiddleware, allow_origins=list(_origins),\n    allow_credentials=True, allow_methods=[\"*\"], allow_headers=[\"*\"],\n)\n" + middleware_code)

with open('server/main.py', 'w', encoding='utf-8') as f:
    f.write(content)
