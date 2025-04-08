from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from requests import Session
from api import file_manager,article_retriever,get_metadata, Image_extractor,table_extractor,combined_extractor,common_word_analysis,pdf_filter,term_extractor
from auth_utils import get_current_user
from create_project import project_router
from models import Base, User, UserCreate
from utils1 import create_access_token, generate_otp, generate_user_id, get_db, send_verification_email
from fastapi import FastAPI
from api import article_retriever,get_metadata, Image_extractor,table_extractor,combined_extractor,common_word_analysis,pdf_filter,term_extractor
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from models import User, UserCreate,Base
from utils1 import get_db, pwd_context, SECRET_KEY, ALGORITHM, generate_user_id, generate_otp, create_access_token, create_verification_token, send_verification_email, engine 
from pydantic import BaseModel
app = FastAPI()
#file manager
app.include_router(file_manager.router,prefix="/downloads",tags=["file_manager"],dependencies=[Depends(get_current_user)])
#term extreactor
app.include_router(term_extractor.router,prefix="/extract-terms",tags=["Term-Extractor"],dependencies=[Depends(get_current_user)])
# Article Retrieval Module
app.include_router(article_retriever.router, prefix="/articles", tags=["Article Retriver"],dependencies=[Depends(get_current_user)])
# get meta data 
app.include_router(get_metadata.router,prefix="/extract-metadata",tags=["Get Details of pdf files "],dependencies=[Depends(get_current_user)])
#common word analysis module
app.include_router(common_word_analysis.router,prefix="/common-word-analysis",tags=["Common Word Analysis"],dependencies=[Depends(get_current_user)])
# Recent Searches Module
app.include_router(combined_extractor.router,prefix="/extract-all",tags=["Combined Extractor"],dependencies=[Depends(get_current_user)])
#table extractor module
app.include_router(table_extractor.router,prefix="/tables",tags=["Table Extractor"],dependencies=[Depends(get_current_user)])

# Image Extraction Module
app.include_router(Image_extractor.router, prefix="/images", tags=["PDF Image Extractor"],dependencies=[Depends(get_current_user)])
#csv  file manger Module
# app.include_router(csv_manager.router, prefix="/csv-manager", tags=["CSV Manager"])
#filter pdf 
app.include_router(pdf_filter.router,prefix="/filter-pdf",tags=["PDF Filter"],dependencies=[Depends(get_current_user)])


app.include_router(project_router.router, prefix="/projects", tags=["User Projects"], dependencies=[Depends(get_current_user)])
@app.get("/")
def root():
    return {"message": "Welcome to VBP FastAPI Backend"}



@app.post("/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if email already exists
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Generate custom user_id
    user_id = generate_user_id(user.first_name)

    # Generate OTP
    otp = generate_otp()

    # Hash password
    hashed_password = pwd_context.hash(user.password)

    # Create new user
    new_user = User(
        user_id=user_id,
        first_name=user.first_name,
        last_name=user.last_name,
        number=user.number,
        email=user.email,
        password_hash=hashed_password,
        is_verified=False,
        otp=otp
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Send OTP via email
    success, message =send_verification_email(new_user.email, otp)
    if success:
        print(f"OTP resent successfully to {new_user.email}: {message}")
        return {"message": "User registered successfully. Please check your email for OTP."}
    else:
        print(f"Failed to send OTP to {new_user.email}: {message}")     
        raise HTTPException(status_code=500, detail="Failed to send OTP email")
    # Send verification email                   

# New Pydantic model for login
class LoginRequest(BaseModel):
    email: str
    password: str

# @app.post("/login")
# async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.email == login_data.email).first()
#     if not user or not pwd_context.verify(login_data.password, user.password_hash) or not user.is_verified:
#         raise HTTPException(status_code=401, detail="Invalid credentials or email not verified")

#     access_token = create_access_token(data={"sub": user.email})
#     return {"access_token": access_token, "token_type": "bearer", "user_id": user.user_id}


from fastapi.security import OAuth2PasswordRequestForm

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.password_hash) or not user.is_verified:
        raise HTTPException(status_code=401, detail="Invalid credentials or email not verified")

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer", "user_id": user.user_id}

@app.get("/verify-otp")
async def verify_otp(email: str, otp: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.otp == otp:
        user.is_verified = True
        user.otp = None  # Clear OTP after verification
        db.commit()
        return {"message": "Email verified successfully"}
    else:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
Base.metadata.create_all(bind=engine)