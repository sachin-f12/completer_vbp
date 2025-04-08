from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class ShowUser(BaseModel):
    username: str
    email: str
    class Config:
        orm_mode = True
