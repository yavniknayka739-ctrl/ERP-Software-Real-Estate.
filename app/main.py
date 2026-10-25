from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)
from app.api import auth_routes
app.include_router(auth_routes.router)
from app.api import commercial
app.include_router(commercial.router)
from app.api import dashboard
app.include_router(dashboard.router)
from app.api import activities
app.include_router(activities.router)
from app.api import clients, projects
app.include_router(clients.router)
app.include_router(projects.router)
from app.api import demo
app.include_router(demo.router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
from app.core.csrf import generate_csrf_token
from fastapi import HTTPException, status
@app.middleware("http")
async def csrf_middleware(request: Request, call_next):
    if request.method in ["POST", "PUT", "DELETE", "PATCH"] and not request.url.path.startswith("/api/"):
        # Handle CSRF only for cookie based browser interactions, not purely stateless APIs if any.
        # We need to manually parse the body. Since we cannot await request.form() in middleware
        # easily without consuming the stream, we will just use a dependency in the form endpoints
        # or handle it manually. Wait, Starlette middleware body consumption is tricky.
        pass
    response = await call_next(request)
    return response


templates = Jinja2Templates(directory="app/templates")

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(request, "index.html", {"request": request, "demo_mode": settings.DEMO_MODE})
