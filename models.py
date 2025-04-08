from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship


Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), unique=True, index=True)  # Specify length (e.g., 255)
    first_name = Column(String(100))  # Specify length
    last_name = Column(String(100))   # Specify length
    number = Column(String(20))       # Specify length (e.g., for phone number)
    email = Column(String(255), unique=True, index=True)  # Specify length
    password_hash = Column(String(255))  # Specify length
    is_verified = Column(Boolean, default=False)
    otp = Column(String(4), nullable=True)  # Specify length (4 digits for OTP)
    created_at = Column(DateTime)
    # models.py (inside User class)
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")


#----------------------projects----------------------------------------#
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

# models.py

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(100), unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(100))
    description = Column(String(255), nullable=True)

    user = relationship("User", back_populates="projects")

    
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    number: str
    email: str
    password: str