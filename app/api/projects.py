from fastapi import APIRouter, Depends, Request, Form
from sqlalchemy.orm import Session
from app.db.tenant import get_tenant_db
from app.core.auth import require_role
from app.core.csrf import verify_csrf
from app.models.user import RoleEnum
from app.models.client_project import Project, Client, ProjectStatus
from app.models.stage_activity import ProjectStage
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/projects", tags=["projects"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def list_projects(
    request: Request,
    db: Session = Depends(get_tenant_db),
    user = Depends(require_role([RoleEnum.ADMIN, RoleEnum.MANAGER, RoleEnum.TECHNICAL, RoleEnum.COMMERCIAL]))
):
    projects = db.query(Project).order_by(Project.id.desc()).all()
    return templates.TemplateResponse(request, "projects/list.html", {"request": request, "projects": projects, "user": user})

@router.get("/new", response_class=HTMLResponse)
async def new_project_form(
    request: Request,
    db: Session = Depends(get_tenant_db),
    user = Depends(require_role([RoleEnum.ADMIN, RoleEnum.MANAGER]))
):
    clients = db.query(Client).all()
    return templates.TemplateResponse(request, "projects/form.html", {"request": request, "clients": clients, "user": user})

@router.post("/new")
async def create_project(
    request: Request,
    client_id: int = Form(...),
    title: str = Form(...),
    description: str = Form(None),
    db: Session = Depends(get_tenant_db),
    csrf_valid: bool = Depends(verify_csrf),
    user = Depends(require_role([RoleEnum.ADMIN, RoleEnum.MANAGER]))
):
    project = Project(client_id=client_id, title=title, description=description)
    db.add(project)
    db.flush() # flush to get project.id

    # Auto-generate default stages
    stage_names = ["Stage A", "Stage B", "Stage C"]
    for name in stage_names:
        stage = ProjectStage(project_id=project.id, name=name)
        db.add(stage)

    db.commit()
    return RedirectResponse("/projects", status_code=303)

@router.get("/{project_id}", response_class=HTMLResponse)
async def view_project(
    project_id: int,
    request: Request,
    db: Session = Depends(get_tenant_db),
    user = Depends(require_role([RoleEnum.ADMIN, RoleEnum.MANAGER, RoleEnum.TECHNICAL, RoleEnum.COMMERCIAL]))
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return HTMLResponse("Project not found", status_code=404)
    return templates.TemplateResponse(request, "projects/view.html", {"request": request, "project": project, "user": user})
