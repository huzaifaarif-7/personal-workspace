import re

with open('server/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add app.state.limiter
if "app.state.limiter =" not in content:
    content = content.replace(
        "app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)",
        "from .auth_routes import limiter\napp.state.limiter = limiter\napp.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)"
    )

with open('server/main.py', 'w', encoding='utf-8') as f:
    f.write(content)
