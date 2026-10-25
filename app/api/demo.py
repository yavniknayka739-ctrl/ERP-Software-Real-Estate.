import uuid
from fastapi import APIRouter, Request, Response
from fastapi.responses import RedirectResponse
from app.core.config import settings
import os

router = APIRouter()

@router.get("/demo")
async def start_demo(request: Request, response: Response):
    if not settings.DEMO_MODE:
        return RedirectResponse("/")

    # Generate a new unique ID for this visitor's demo session
    demo_id = str(uuid.uuid4())

    # Create redirect response to the demo login page
    redirect = RedirectResponse("/login", status_code=303)
    redirect.set_cookie(key="demo_id", value=demo_id, httponly=True, max_age=60*60*24) # 24h
    return redirect

@router.get("/demo/reset")
async def reset_demo(request: Request):
    if not settings.DEMO_MODE:
        return RedirectResponse("/")

    demo_id = request.cookies.get("demo_id")
    if demo_id:
        db_path = f"./demo_dbs/demo_{demo_id}.db"
        if os.path.exists(db_path):
            os.remove(db_path)

    return RedirectResponse("/demo")
