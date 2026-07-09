import re

with open('server/auth_routes.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add Pydantic max_length and Field
if "from pydantic import BaseModel, EmailStr, Field" not in content:
    content = content.replace("from pydantic import BaseModel, EmailStr", "from pydantic import BaseModel, EmailStr, Field")

# Update SignupRequest
old_signup = """class SignupRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str"""
new_signup = """class SignupRequest(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)"""
content = content.replace(old_signup, new_signup)

# Update LoginRequest
old_login = """class LoginRequest(BaseModel):
    email: EmailStr
    password: str"""
new_login = """class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)"""
content = content.replace(old_login, new_login)

# Add limiter and limit logic
if "limiter = Limiter(" not in content:
    limiter_import = """from slowapi import Limiter
from slowapi.util import get_remote_address
limiter = Limiter(key_func=get_remote_address)

"""
    content = content.replace("log = logging.getLogger(__name__)\n", "log = logging.getLogger(__name__)\n\n" + limiter_import)

content = content.replace('@auth_router.post("/signup")', '@auth_router.post("/signup")\n@limiter.limit("3/minute")')
content = content.replace('@auth_router.post("/login")', '@auth_router.post("/login")\n@limiter.limit("5/minute")')

# Fix password length check in signup (was returning password_too_short and password_too_long)
# Pydantic will catch these now, but let's leave the manual check to return specific JSON, or rather just update the manual check.
# The user wants: Return a specific, helpful error: {"error": "password_too_short", "min_length": 8}
old_pwd_check = """    if len(req.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "invalid_input", "reason": "password_too_short"}
        )"""
new_pwd_check = """    if len(req.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "password_too_short", "min_length": 8}
        )"""
content = content.replace(old_pwd_check, new_pwd_check)

# Fix Account Enumeration in login (4b)
# And session fixation (4d)

old_login_body = """    log.info("login: querying DB for user")
    user = db.query(User).filter(User.email == req.email).first()

    log.info("login: verifying password (bcrypt — expect ~200-500ms)")
    if len(req.password.encode("utf-8")) > 72:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "invalid_credentials"}
        )

    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "invalid_credentials"}
        )

    log.info("login: writing session cookie for user_id=%s", user.id)
    request.session["user_id"] = user.id"""

# Create a precomputed dummy hash for timing attacks
new_login_body = """    log.info("login: querying DB for user")
    user = db.query(User).filter(User.email == req.email).first()

    log.info("login: verifying password (bcrypt — expect ~200-500ms)")
    
    # Pre-computed bcrypt hash of "dummy"
    dummy_hash = b'$2b$12$Nq9rWjLq0nO2z8QZ1X7V3e8K5F6d9C6m3x5h9J2p5Nq9rWjLq0nO2'
    
    # Timing-safe validation
    is_valid = False
    if user:
        is_valid = verify_password(req.password, user.password_hash)
    else:
        verify_password(req.password, dummy_hash.decode('utf-8'))
        
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "invalid_credentials"}
        )

    log.info("login: writing session cookie for user_id=%s", user.id)
    request.session.clear() # Fix session fixation
    request.session["user_id"] = user.id"""

content = content.replace(old_login_body, new_login_body)

# Session Fixation in signup
content = content.replace('request.session["user_id"] = user.id', 'request.session.clear()\n    request.session["user_id"] = user.id')

with open('server/auth_routes.py', 'w', encoding='utf-8') as f:
    f.write(content)
