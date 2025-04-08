import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from jose import JWTError,jwt
from passlib.context import CryptContext
import random
import string
import smtplib
from email.message import EmailMessage
from models import User, UserCreate
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from settings import BASE_DIR
# Database Setup
# Database Setup (MySQL)
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:root@localhost:5432/holly"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Settings
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def generate_user_id(first_name: str) -> str:
    base = first_name.lower().replace(" ", "")
    while True:
        number = ''.join(random.choices(string.digits, k=3))
        user_id = f"{base}{number}"
        db = SessionLocal()
        if not db.query(User).filter(User.user_id == user_id).first():
            db.close()
            return user_id
        db.close()

def generate_otp() -> str:
    return ''.join(random.choices(string.digits, k=4))

def create_access_token(data: dict) -> str:
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def create_verification_token(user_id: int) -> str:
    return jwt.encode({"sub": user_id}, SECRET_KEY, algorithm=ALGORITHM)

def send_verification_email(email: str, otp: str):

    # Sender email configuration
    sender_email = "naveenpatidar4513@gmail.com"
    sender_password = "qpfw mlkg whcj qzuu"  # App-specific password
    
    # Create email message
    msg = MIMEMultipart('alternative')
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = 'Email Verification - Emedical'

    html = f"""<html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background-color: #f4f4f4;
                        margin: 0;
                        padding: 20px;
                    }}
                    .container {{
                        background-color: #ffffff;
                        border-radius: 8px;
                        padding: 20px;
                        max-width: 600px;
                        margin: auto;
                        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    }}
                    h1 {{
                        color: #333;
                    }}
                    p {{
                        color: #555;
                    }}
                    .otp {{
                        font-size: 24px;
                        color: #0066cc;
                        font-weight: bold;
                    }}
                    .footer {{
                        font-size: 12px;
                        color: #888;
                        text-align: center;
                        margin-top: 20px;
                        border-top: 1px solid #ddd;
                        padding-top: 10px;
                    }}
                    a {{
                        color: #1a0dab;
                        text-decoration: none;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Welcome to Emedical</h1>
                    <p>Thank you for registering with us. Please use the following OTP to verify your email:</p>
                    <p class="otp">{otp}</p>
                    <p>Username: {email}</p>
                    <p>This OTP is valid for 10 minutes. Do not share it with anyone.</p>
                    <p>If you didn't request this, please ignore this email or contact support@etransport.app</p>
                </div>
                <div class="footer">
                    <p>© 2025 Etransport, Inc. All rights reserved.<br>
                       IT Park, Indore, M.P. India<br>
                       <a href="https://emedical.app/unsubscribe">Unsubscribe</a></p>
                </div>
            </body>
        </html>"""
    
    # Attach HTML content
    part = MIMEText(html, 'html')
    msg.attach(part)

    try:
        # Connect to SMTP server
        with smtplib.SMTP('smtp.gmail.com', 587) as s:
            s.starttls()
            s.login(sender_email, sender_password)
            s.sendmail(sender_email, email, msg.as_string())
        return True, "Verification email sent successfully"
    
    except smtplib.SMTPAuthenticationError:
        return False, "Email authentication failed. Please check credentials"
    except smtplib.SMTPRecipientsRefused:
        return False, "Email address rejected by server"
    except smtplib.SMTPException as e:
        return False, f"SMTP error occurred: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error occurred: {str(e)}"
    
#for dynamic user_name/user_project folder structure
def get_project_path(user_id, project_id):
    return Path(f"user_{user_id}/project_{project_id}")
