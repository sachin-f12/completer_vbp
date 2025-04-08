from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Project, User
from utils1 import get_db, get_project_path
from auth_utils import get_current_user
from schemas import ProjectCreate, ProjectOut
import uuid
import os

router = APIRouter()

# Route to create a new project
@router.post("/create", response_model=ProjectOut)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project_id = str(uuid.uuid4())[:8]  # Short unique ID
    new_project = Project(
        project_id=project_id,
        name=project.name,
        description=project.description,
        user_id=current_user.user_id
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    # Create project folder on project creation
    input_dir = get_project_path(current_user.user_id, project_id)
    os.makedirs(input_dir, exist_ok=True)

    return new_project

# Route to list all projects for a user
@router.get("/", response_model=list[ProjectOut])
def get_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Project).filter(Project.user_id == current_user.user_id).all()

# Route to fetch a specific project
@router.get("/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(
        Project.project_id == project_id,
        Project.user_id == current_user.user_id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

# Route to get the folder path of a project
@router.get("/{project_id}/path")
def get_project_storage_path(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(
        Project.project_id == project_id,
        Project.user_id == current_user.user_id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    input_dir = get_project_path(current_user.user_id, project_id)
    os.makedirs(input_dir, exist_ok=True)

    return {"project_path": input_dir}
