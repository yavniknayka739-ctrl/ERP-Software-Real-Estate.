from sqlalchemy import Column, Integer, String, Boolean, Enum
from app.db.database import Base
import enum

class RoleEnum(str, enum.Enum):
    ADMIN = "Admin"
    TECHNICAL = "Technical Employee"
    COMMERCIAL = "Commercial User"
    MANAGER = "Manager"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
    is_active = Column(Boolean, default=True)
