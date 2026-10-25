import secrets
from fastapi import Request, Form, HTTPException, status, Depends
from typing import Optional

def generate_csrf_token() -> str:
    return secrets.token_hex(32)

def verify_csrf(request: Request, csrf_token: str = Form(...)):
    cookie_csrf = request.cookies.get("csrf_token")
    if not cookie_csrf or not csrf_token or cookie_csrf != csrf_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CSRF token validation failed")
    return True
