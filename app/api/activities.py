from fastapi import APIRouter, Depends, Request, Form
from sqlalchemy.orm import Session
from app.db.tenant import get_tenant_db
from app.core.auth import require_role
from app.core.csrf import verify_csrf
from app.models.user import RoleEnum, User
from app.models.client_project import Project
from app.models.stage_activity import ProjectStage, Activity, ActivityTemplate, ActivityHistory, ActivityStatus
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, timezone

router = APIRouter(prefix="/activities", tags=["activities"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/templates", response_class=HTMLResponse)
async def list_templates(
    request: Request,
    db: Session = Depends(get_tenant_db),
    user = Depends(require_role([RoleEnum.ADMIN, RoleEnum.MANAGER]))
):
    templates_list = db.query(ActivityTemplate).all()
    return templates.TemplateResponse(request, "activities/templates.html", {"request": request, "templates": templates_list, "user": user})

@router.post("/templates/new")
async def create_template(
    request: Request,
    name: str = Form(...),
    description: str = Form(None),
    db: Session = Depends(get_tenant_db),
    csrf_valid: bool = Depends(verify_csrf),
    user = Depends(require_role([RoleEnum.ADMIN, RoleEnum.MANAGER]))
):
    template = ActivityTemplate(name=name, description=description)
    db.add(template)
    db.commit()
    return RedirectResponse("/activities/templates", status_code=303)

@router.post("/assign/{stage_id}")
async def assign_activity(
    stage_id: int,
    request: Request,
    template_id: int = Form(None),
    name: str = Form(None),
    description: str = Form(None),
    assigned_to: int = Form(None),
    db: Session = Depends(get_tenant_db),
    csrf_valid: bool = Depends(verify_csrf),
    user = Depends(require_role([RoleEnum.ADMIN, RoleEnum.MANAGER]))
):
    stage = db.query(ProjectStage).filter(ProjectStage.id == stage_id).first()
    if not stage:
        return HTMLResponse("Stage not found", status_code=404)

    if template_id:
        template = db.query(ActivityTemplate).filter(ActivityTemplate.id == template_id).first()
        if template:
            name = template.name
            description = template.description

    activity = Activity(
        stage_id=stage_id,
        name=name,
        description=description,
        assigned_to=assigned_to
    )
    db.add(activity)
    db.commit()
    return RedirectResponse(f"/projects/{stage.project_id}", status_code=303)

@router.post("/{activity_id}/update_status")
async def update_activity_status(
    activity_id: int,
    request: Request,
    status: ActivityStatus = Form(...),
    notes: str = Form(None),
    db: Session = Depends(get_tenant_db),
    csrf_valid: bool = Depends(verify_csrf),
    user = Depends(require_role([RoleEnum.ADMIN, RoleEnum.MANAGER, RoleEnum.TECHNICAL]))
):
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        return HTMLResponse("Activity not found", status_code=404)

    old_status = activity.status.value

    if status == ActivityStatus.COMPLETED and activity.status != ActivityStatus.COMPLETED:
        activity.completion_date = datetime.now(timezone.utc)
    elif status != ActivityStatus.COMPLETED:
        # Reopening or changing to pending/in progress
        # we don't clear completion_date per requirements ("preserve its history where practical")
        pass

    activity.status = status
    if notes:
        activity.notes = notes

    # Log history
    history = ActivityHistory(
        activity_id=activity.id,
        old_status=old_status,
        new_status=status.value,
        changed_by=user.id
    )
    db.add(history)
    db.commit()

    return RedirectResponse(f"/projects/{activity.stage.project_id}", status_code=303)
