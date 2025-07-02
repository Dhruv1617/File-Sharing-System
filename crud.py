from sqlalchemy.orm import Session
from models import User, UploadedFile
from schemas import UserCreate
from auth import get_password_hash

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, password_hash=hashed_password, role="client")
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_file(db: Session, filename: str, filepath: str, user_id: int):
    db_file = UploadedFile(filename=filename, filepath=filepath, uploaded_by=user_id)
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

def get_files(db: Session):
    return db.query(UploadedFile).all()