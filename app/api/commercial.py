from fastapi import APIRouter, Depends, Request, Form
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.tenant import get_tenant_db
from app.core.auth import require_role
from app.core.csrf import verify_csrf
from app.models.user import RoleEnum
from app.models.client_project import Project
from app.models.financial import Payment, Expense, PaymentStatus
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, date
from decimal import Decimal

router = APIRouter(prefix="/commercial", tags=["commercial"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/project/{project_id}", response_class=HTMLResponse)
async def view_financials(
    project_id: int,
    request: Request,
    db: Session = Depends(get_tenant_db),
    user = Depends(require_role([RoleEnum.ADMIN, RoleEnum.COMMERCIAL]))
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return HTMLResponse("Project not found", status_code=404)

    total_received = sum(p.amount for p in project.payments if p.status == PaymentStatus.PAID)
    total_expenses = sum(e.amount for e in project.expenses)
    outstanding = project.agreed_amount - total_received
    profit = project.agreed_amount - total_expenses

    overpaid_warning = outstanding < 0

    return templates.TemplateResponse(request, "commercial/project.html", {
        "request": request,
        "project": project,
        "user": user,
        "total_received": total_received,
        "total_expenses": total_expenses,
        "outstanding": outstanding,
        "profit": profit,
        "overpaid_warning": overpaid_warning
    })

@router.post("/project/{project_id}/payment")
async def add_payment(
    project_id: int,
    request: Request,
    amount: Decimal = Form(...),
    description: str = Form(...),
    expected_date: date = Form(...),
    status: PaymentStatus = Form(...),
    actual_date: date = Form(None),
    db: Session = Depends(get_tenant_db),
    csrf_valid: bool = Depends(verify_csrf),
    user = Depends(require_role([RoleEnum.ADMIN, RoleEnum.COMMERCIAL]))
):
    payment = Payment(
        project_id=project_id,
        amount=amount,
        description=description,
        expected_date=expected_date,
        actual_date=actual_date,
        status=status
    )
    db.add(payment)
    db.commit()
    return RedirectResponse(f"/commercial/project/{project_id}", status_code=303)

@router.post("/project/{project_id}/expense")
async def add_expense(
    project_id: int,
    request: Request,
    category: str = Form(...),
    amount: Decimal = Form(...),
    expense_date: date = Form(...),
    notes: str = Form(None),
    db: Session = Depends(get_tenant_db),
    csrf_valid: bool = Depends(verify_csrf),
    user = Depends(require_role([RoleEnum.ADMIN, RoleEnum.COMMERCIAL]))
):
    expense = Expense(
        project_id=project_id,
        category=category,
        amount=amount,
        expense_date=expense_date,
        notes=notes
    )
    db.add(expense)
    db.commit()
    return RedirectResponse(f"/commercial/project/{project_id}", status_code=303)
