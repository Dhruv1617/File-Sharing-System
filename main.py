from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import FileResponse as FastAPIFileResponse
from sqlalchemy.orm import Session
from models import Base, UploadedFile, User
from schemas import UserCreate, UserResponse, Token, FileResponse as FileSchemaResponse, DownloadLink
from auth import create_access_token, get_current_user, verify_password
from crud import create_user, get_user_by_email, create_file, get_files
from utils import allowed_file, send_verification_email, generate_secure_url, decode_secure_url
from database import engine, get_db
from config import Config
import os
from jose import jwt

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "API is running"}

# Create database tables
Base.metadata.create_all(bind=engine)

@app.post("/signup", response_model=UserResponse)
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = create_user(db, user)
    token = jwt.encode({"email": user.email}, Config.SECRET_KEY, algorithm="HS256")
    send_verification_email(user.email, token)
    return new_user

@app.get("/verify-email/{token}")
async def verify_email(token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        email = payload.get("email")
        user = get_user_by_email(db, email)
        if not user:
            raise HTTPException(status_code=400, detail="Invalid token")
        user.is_verified = True
        db.commit()
        return {"message": "Email verified successfully"}
    except jwt.JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

@app.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_verified and user.role == "client":
        raise HTTPException(status_code=401, detail="Email not verified")
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/upload-file", response_model=FileSchemaResponse)
async def upload_file(file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "ops":
        raise HTTPException(status_code=403, detail="Only Ops Users can upload files")
    if not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="Invalid file type")
    filename = file.filename
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    with open(filepath, "wb") as f:
        f.write(await file.read())
    db_file = create_file(db, filename, filepath, current_user.id)
    return db_file

@app.get("/list-files", response_model=list[FileSchemaResponse])
async def list_files(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "client":
        raise HTTPException(status_code=403, detail="Only Client Users can list files")
    files = get_files(db)
    return files

@app.get("/download-file/{assignment_id}", response_model=DownloadLink)
async def download_file(assignment_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "client":
        raise HTTPException(status_code=403, detail="Only Client Users can download files")
    file = db.query(UploadedFile).filter(UploadedFile.id == assignment_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    secure_url = generate_secure_url(assignment_id)
    return {"download_link": f"http://localhost:8000/download/{secure_url}", "message": "success"}

@app.get("/download/{token}")
async def serve_file(token: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "client":
        raise HTTPException(status_code=403, detail="Only Client Users can access this URL")
    assignment_id = decode_secure_url(token)
    if not assignment_id:
        raise HTTPException(status_code=400, detail="Invalid or expired download link")
    file = db.query(File).filter(File.id == assignment_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    return FastAPIFileResponse(file.filepath, filename=file.filename)
