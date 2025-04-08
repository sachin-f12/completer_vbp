from pydantic import BaseModel


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None

class ProjectOut(BaseModel):
    project_id: str
    name: str
    description: str | None

    class Config:
        orm_mode = True
