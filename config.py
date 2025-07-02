import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY","default_key")  # For JWT and URL encryption
    DATABASE_URL = os.getenv("DATABASE_URL")
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), "uploads")
    ALLOWED_EXTENSIONS = {"pptx", "docx", "xlsx"}
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")