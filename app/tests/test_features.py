import pytest
from app.models.client_project import Client, Project, ProjectStatus
from app.models.stage_activity import ProjectStage, Activity, ActivityStatus
from app.models.financial import Payment, Expense, PaymentStatus

def test_create_client(auth_client, db_session):
    auth_client.cookies.set("csrf_token", "test-token")
    response = auth_client.post("/clients/new", data={
        "name": "Test Client",
        "mobile": "1234567890",
        "email": "test@test.com",
        "company": "",
        "notes": "",
        "csrf_token": "test-token"
    })
    assert response.status_code == 200 # Redirects back to list

    client = db_session.query(Client).filter(Client.name == "Test Client").first()
    assert client is not None
    assert client.mobile == "1234567890"

def test_create_project_with_default_stages(auth_client, db_session):
    auth_client.cookies.set("csrf_token", "test-token")
    client = Client(name="P Client", mobile="123")
    db_session.add(client)
    db_session.commit()

    response = auth_client.post("/projects/new", data={
        "client_id": client.id,
        "title": "Test Project",
        "description": "Desc",
        "csrf_token": "test-token"
    })
    assert response.status_code == 200

    project = db_session.query(Project).filter(Project.title == "Test Project").first()
    assert project is not None

    stages = db_session.query(ProjectStage).filter(ProjectStage.project_id == project.id).all()
    assert len(stages) == 3

def test_activity_progress_calculation(auth_client, db_session):
    client = Client(name="C1", mobile="123")
    db_session.add(client)
    db_session.commit()
    project = Project(client_id=client.id, title="P1")
    db_session.add(project)
    db_session.flush()
    s1 = ProjectStage(project_id=project.id, name="S1")
    db_session.add(s1)
    db_session.commit()

    response = auth_client.get("/dashboard/tech")
    assert response.status_code == 200

    a1 = Activity(stage_id=s1.id, name="A1", status=ActivityStatus.COMPLETED)
    a2 = Activity(stage_id=s1.id, name="A2", status=ActivityStatus.PENDING)
    db_session.add_all([a1, a2])
    db_session.commit()

    response = auth_client.get("/dashboard/tech")
    assert response.status_code == 200
    assert b"50.0%" in response.content

def test_financial_calculations_and_overpayment(comm_client, db_session):
    comm_client.cookies.set("csrf_token", "test-token")
    client = Client(name="C1", mobile="123")
    db_session.add(client)
    db_session.commit()
    project = Project(client_id=client.id, title="P1", agreed_amount=1000.00)
    db_session.add(project)
    db_session.commit()

    response = comm_client.post(f"/commercial/project/{project.id}/payment", data={
        "amount": 1200.00,
        "description": "Advance",
        "expected_date": "2024-01-01",
        "status": "Paid",
        "actual_date": "2024-01-01",
        "csrf_token": "test-token"
    })

    response2 = comm_client.get(f"/commercial/project/{project.id}")
    assert b"Warning" in response2.content
    assert b"-200.0" in response2.content
