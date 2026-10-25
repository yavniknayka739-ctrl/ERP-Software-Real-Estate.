from fastapi import APIRouter, Depends, Request, Form
from sqlalchemy.orm import Session
from app.db.tenant import get_tenant_db
from app.core.auth import require_role
from app.core.csrf import verify_csrf
from app.models.user import RoleEnum
from app.models.client_project import Client
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/clients", tags=["clients"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def list_clients(
    request: Request,
    db: Session = Depends(get_tenant_db),
    user = Depends(require_role([RoleEnum.ADMIN, RoleEnum.MANAGER, RoleEnum.TECHNICAL, RoleEnum.COMMERCIAL]))
):
    clients = db.query(Client).order_by(Client.id.desc()).all()
    return templates.TemplateResponse(request, "clients/list.html", {"request": request, "clients": clients, "user": user})

@router.get("/new", response_class=HTMLResponse)
async def new_client_form(
    request: Request,
    user = Depends(require_role([RoleEnum.ADMIN, RoleEnum.MANAGER, RoleEnum.COMMERCIAL]))
):
    return templates.TemplateResponse(request, "clients/form.html", {"request": request, "user": user})

@router.post("/new")
async def create_client(
    request: Request,
    name: str = Form(...),
    mobile: str = Form(...),
    email: str = Form(None),
    company: str = Form(None),
    notes: str = Form(None),
    db: Session = Depends(get_tenant_db),
    csrf_valid: bool = Depends(verify_csrf),
    user = Depends(require_role([RoleEnum.ADMIN, RoleEnum.MANAGER, RoleEnum.COMMERCIAL]))
):
    client = Client(name=name, mobile=mobile, email=email, company=company, notes=notes)
    db.add(client)
    db.commit()
    return RedirectResponse("/clients", status_code=303)

@router.get("/{client_id}", response_class=HTMLResponse)
async def view_client(
    client_id: int,
    request: Request,
    db: Session = Depends(get_tenant_db),
    user = Depends(require_role([RoleEnum.ADMIN, RoleEnum.MANAGER, RoleEnum.TECHNICAL, RoleEnum.COMMERCIAL]))
):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        return HTMLResponse("Client not found", status_code=404)
    return templates.TemplateResponse(request, "clients/view.html", {"request": request, "client": client, "user": user})
