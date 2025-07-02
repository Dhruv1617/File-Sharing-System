import unittest
from fastapi.testclient import TestClient
from main import app, get_db
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Base, User, File
from auth import create_access_token
import os

class FileOpsTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("mysql+mysqlconnector://root:mysqlpass@localhost:3306/test_db")
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.client = TestClient(app)

        def override_get_db():
            db = self.SessionLocal()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db

        db = self.SessionLocal()
        ops_user = User(email="ops@example.com", role="ops", is_verified=True, password_hash=get_password_hash("password123"))
        client_user = User(email="client@example.com", role="client", is_verified=True, password_hash=get_password_hash("password123"))
        db.add_all([ops_user, client_user])
        db.commit()
        db.close()
        self.ops_token = create_access_token({"sub": str(ops_user.id)})
        self.client_token = create_access_token({"sub": str(client_user.id)})

    def tearDown(self):
        Base.metadata.drop_all(self.engine)

    def test_upload_file_ops(self):
        with open("test.docx", "wb") as f:
            f.write(b"Dummy content")
        with open("test.docx", "rb") as f:
            response = self.client.post("/upload-file", files={"file": ("test.docx", f)}, headers={"Authorization": f"Bearer {self.ops_token}"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["filename"], "test.docx")
        os.remove("test.docx")

    def test_upload_file_client(self):
        with open("test.docx", "wb") as f:
            f.write(b"Dummy content")
        with open("test.docx", "rb") as f:
            response = self.client.post("/upload-file", files={"file": ("test.docx", f)}, headers={"Authorization": f"Bearer {self.client_token}"})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["detail"], "Only Ops Users can upload files")
        os.remove("test.docx")

    def test_list_files_client(self):
        response = self.client.get("/list-files", headers={"Authorization": f"Bearer {self.client_token}"})
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_download_file_client(self):
        db = self.SessionLocal()
        file = File(filename="test.docx", filepath="uploads/test.docx", uploaded_by=1)
        db.add(file)
        db.commit()
        file_id = file.id
        db.close()
        response = self.client.get(f"/download-file/{file_id}", headers={"Authorization": f"Bearer {self.client_token}"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("download_link", response.json())

if __name__ == "__main__":
    unittest.main()