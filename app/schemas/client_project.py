from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from app.models.client_project import ProjectStatus
from decimal import Decimal

class ClientBase(BaseModel):
    name: str
    mobile: str
    email: Optional[str] = None
    company: Optional[str] = None
    notes: Optional[str] = None

class ClientCreate(ClientBase):
    pass

class ClientUpdate(ClientBase):
    pass

class ClientOut(ClientBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None
    req_start_date: Optional[date] = None
    req_end_date: Optional[date] = None
    actual_start_date: Optional[date] = None
    expected_end_date: Optional[date] = None
    manager_id: Optional[int] = None
    assigned_team: Optional[str] = None
    status: ProjectStatus = ProjectStatus.NOT_STARTED
    # Financial fields should only be managed by commercial roles, but included in schema for those with access
    agreed_amount: Decimal = Decimal('0.00')
    payment_terms: Optional[str] = None

class ProjectCreate(ProjectBase):
    client_id: int

class ProjectUpdate(ProjectBase):
    pass

class ProjectOut(ProjectBase):
    id: int
    client_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
