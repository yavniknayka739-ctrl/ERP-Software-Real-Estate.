import argparse
from app.db.database import SessionLocal
from app.models.user import User, RoleEnum
from app.core.security import get_password_hash

def create_admin(username, password):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if user:
            print(f"User {username} already exists.")
            return

        hashed_password = get_password_hash(password)
        admin = User(
            username=username,
            hashed_password=hashed_password,
            role=RoleEnum.ADMIN,
            is_active=True
        )
        db.add(admin)
        db.commit()
        print(f"Administrator {username} created successfully.")
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create an initial administrator")
    parser.add_argument("username", help="Admin username")
    parser.add_argument("password", help="Admin password")
    args = parser.parse_args()

    create_admin(args.username, args.password)
