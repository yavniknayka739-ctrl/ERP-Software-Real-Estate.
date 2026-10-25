import secrets
from fastapi import Request, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.tenant import get_tenant_db
from app.models.user import User

# In-memory session store for simplicity, could be moved to DB or Redis
# Format: {session_id: {"user_id": int, "expires": datetime}}
SESSIONS = {}

def create_session(user_id: int) -> str:
    session_id = secrets.token_urlsafe(32)
    from datetime import datetime, timedelta, timezone
    from app.core.config import settings
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    SESSIONS[session_id] = {"user_id": user_id, "expires": expires}
    return session_id

def get_current_user(request: Request, db: Session = Depends(get_tenant_db)):
    session_id = request.cookies.get("session_id")
    if not session_id or session_id not in SESSIONS:
        return None

    session_data = SESSIONS[session_id]
    from datetime import datetime, timezone
    if session_data["expires"] < datetime.now(timezone.utc):
        del SESSIONS[session_id]
        return None

    user = db.query(User).filter(User.id == session_data["user_id"]).first()
    if not user or not user.is_active:
        return None

    return user

def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Cookie"},
        )
    return current_user

def require_role(roles: list[str]):
    def role_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.role.value not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_checker

def verify_csrf(request: Request):
    if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
        csrf_token = request.cookies.get("csrf_token")
        form_csrf = None
        # We need to extract form_csrf carefully since request.form() is async
        # We'll handle this check directly in the route or via a middleware.
        # Returning None for now, will implement within routes to await form data
        pass
