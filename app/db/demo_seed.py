from datetime import datetime, timedelta, timezone
from decimal import Decimal
from app.models.financial import Payment, PaymentStatus, Expense

from app.db.database import SessionLocal
from app.models.user import User, RoleEnum
from app.core.security import get_password_hash
# Import other models here when created

def seed_demo_db(db):
    # Clear existing users for demo
    db.query(User).delete()

    users = [
        User(username="admin", hashed_password=get_password_hash("admin"), role=RoleEnum.ADMIN),
        User(username="tech", hashed_password=get_password_hash("tech"), role=RoleEnum.TECHNICAL),
        User(username="manager", hashed_password=get_password_hash("manager"), role=RoleEnum.MANAGER),
        User(username="commercial", hashed_password=get_password_hash("commercial"), role=RoleEnum.COMMERCIAL),
    ]
    db.add_all(users)
    db.commit()
    print("Demo DB seeded with base users.")

if __name__ == "__main__":
    db = SessionLocal()
    seed_demo_db(db)
    db.close()

    # Seed Client
    from app.models.client_project import Client, Project, ProjectStatus
    client = Client(name="Acme Real Estate", mobile="555-0199", company="Acme Corp")
    db.add(client)
    db.commit()

    # Seed Project
    project = Project(
        client_id=client.id,
        title="Downtown Office Renovation",
        status=ProjectStatus.IN_PROGRESS,
        agreed_amount=Decimal('500000.00')
    )
    db.add(project)
    db.commit()

    # Auto stages are not created here unless we call the route logic, let's create manually for seed
    from app.models.stage_activity import ProjectStage, Activity, ActivityStatus
    s1 = ProjectStage(project_id=project.id, name="Stage A")
    s2 = ProjectStage(project_id=project.id, name="Stage B")
    s3 = ProjectStage(project_id=project.id, name="Stage C")
    db.add_all([s1, s2, s3])
    db.commit()

    a1 = Activity(stage_id=s1.id, name="Initial Site Survey", status=ActivityStatus.COMPLETED)
    a2 = Activity(stage_id=s1.id, name="Requirements Gathering", status=ActivityStatus.IN_PROGRESS)
    db.add_all([a1, a2])
    db.commit()

    # Seed Financials
    p1 = Payment(project_id=project.id, amount=Decimal('100000.00'), description="Advance", expected_date=datetime.now().date(), actual_date=datetime.now().date(), status=PaymentStatus.PAID)
    e1 = Expense(project_id=project.id, category="Materials", amount=Decimal('25000.00'), expense_date=datetime.now().date())
    db.add_all([p1, e1])
    db.commit()

    print("Seeded realistic demo data.")
