from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.db.tenant import get_tenant_db
from app.core.auth import require_role
from app.models.user import RoleEnum
from app.models.client_project import Project, ProjectStatus
from app.models.stage_activity import Activity, ActivityStatus
from app.models.financial import PaymentStatus
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
templates = Jinja2Templates(directory="app/templates")

def calculate_progress(completed_count, total_count):
    if total_count == 0:
        return "N/A"
    return f"{(completed_count / total_count * 100):.1f}%"

@router.get("/tech", response_class=HTMLResponse)
async def tech_dashboard(
    request: Request,
    db: Session = Depends(get_tenant_db),
    user = Depends(require_role([RoleEnum.ADMIN, RoleEnum.MANAGER, RoleEnum.TECHNICAL]))
):
    total_active = db.query(Project).filter(Project.status.in_([ProjectStatus.IN_PROGRESS, ProjectStatus.NOT_STARTED])).count()
    status_counts = db.query(Project.status, func.count(Project.id)).group_by(Project.status).all()

    # Efficiently load stages and activities to avoid N+1 queries
    all_projects = db.query(Project).options(
        joinedload(Project.stages).joinedload(Activity.stage.property.mapper.class_.activities)
    ).all()

    project_progress = []

    for p in all_projects:
        total_acts = sum(len(s.activities) for s in p.stages)
        comp_acts = sum(1 for s in p.stages for a in s.activities if a.status == ActivityStatus.COMPLETED)

        warn_completed = False
        if total_acts > 0 and comp_acts == total_acts and p.status != ProjectStatus.COMPLETED:
            warn_completed = True

        project_progress.append({
            "project": p,
            "progress": calculate_progress(comp_acts, total_acts),
            "warn_completed": warn_completed
        })

    return templates.TemplateResponse(request, "dashboard/tech.html", {
        "request": request,
        "user": user,
        "total_active": total_active,
        "status_counts": status_counts,
        "project_progress": project_progress
    })

@router.get("/commercial", response_class=HTMLResponse)
async def commercial_dashboard(
    request: Request,
    db: Session = Depends(get_tenant_db),
    user = Depends(require_role([RoleEnum.ADMIN, RoleEnum.COMMERCIAL]))
):
    # Eager load payments and expenses to prevent N+1
    projects = db.query(Project).options(
        joinedload(Project.payments),
        joinedload(Project.expenses)
    ).all()

    total_agreed = sum(p.agreed_amount for p in projects)
    total_received = 0
    total_outstanding = 0
    total_expenses = 0
    total_overdue = 0

    project_summaries = []

    for p in projects:
        received = sum(pay.amount for pay in p.payments if pay.status == PaymentStatus.PAID)
        expenses = sum(e.amount for e in p.expenses)
        overdue = sum(pay.amount for pay in p.payments if pay.status == PaymentStatus.OVERDUE)
        outstanding = p.agreed_amount - received

        total_received += received
        total_expenses += expenses
        total_outstanding += outstanding
        total_overdue += overdue

        project_summaries.append({
            "project": p,
            "received": received,
            "expenses": expenses,
            "outstanding": outstanding,
            "profit": p.agreed_amount - expenses
        })

    return templates.TemplateResponse(request, "dashboard/commercial.html", {
        "request": request,
        "user": user,
        "total_agreed": total_agreed,
        "total_received": total_received,
        "total_outstanding": total_outstanding,
        "total_expenses": total_expenses,
        "total_overdue": total_overdue,
        "total_profit": total_agreed - total_expenses,
        "project_summaries": project_summaries
    })
