from fastapi import APIRouter, Depends, Request, Form, Response
from sqlalchemy.orm import Session
from app.db.tenant import get_tenant_db
from app.models.user import User
from app.core.security import verify_password
from app.core.auth import create_session, SESSIONS
from app.core.csrf import generate_csrf_token
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.core.config import settings

router = APIRouter(tags=["auth"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request, response: Response):
    csrf_token = generate_csrf_token()
    response = templates.TemplateResponse(request, "auth/login.html", {"request": request, "settings": settings, "csrf_token": csrf_token})
    response.set_cookie(key="csrf_token", value=csrf_token, httponly=True)
    return response

@router.post("/login")
async def login(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_tenant_db)
):
    cookie_csrf = request.cookies.get("csrf_token")
    if not cookie_csrf or cookie_csrf != csrf_token:
        return templates.TemplateResponse(request, "auth/login.html", {"request": request, "settings": settings, "error": "CSRF validation failed", "csrf_token": cookie_csrf})

    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(request, "auth/login.html", {"request": request, "settings": settings, "error": "Invalid username or password", "csrf_token": cookie_csrf})

    session_id = create_session(user.id)
    redirect = RedirectResponse("/", status_code=303)
    redirect.set_cookie(key="session_id", value=session_id, httponly=True)
    return redirect

@router.get("/logout")
async def logout(request: Request, response: Response):
    session_id = request.cookies.get("session_id")
    if session_id in SESSIONS:
        del SESSIONS[session_id]
    redirect = RedirectResponse("/", status_code=303)
    redirect.delete_cookie("session_id")
    return redirect
