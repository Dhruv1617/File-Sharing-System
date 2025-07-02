import unittest
from fastapi.testclient import TestClient
from main import app, get_db
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Base, User

class AuthTestCase(unittest.TestCase):
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

    def tearDown(self):
        Base.metadata.drop_all(self.engine)

    def test_signup(self):
        response = self.client.post("/signup", json={"email": "test@example.com", "password": "password123"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["email"] == "test@example.com")

    def test_login_unverified(self):
        self.client.post("/signup", json={"email": "test@example.com", "password": "password123"})
        response = self.client.post("/login", data={"username": "test@example.com", "password": "password123"})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Email not verified")

    def test_login_success(self):
        self.client.post("/signup", json={"email": "test@example.com", "password": "password123"})
        db = self.SessionLocal()
        user = db.query(User).filter(User.email == "test@example.com").first()
        user.is_verified = True
        db.commit()
        db.close()
        response = self.client.post("/login", data={"username": "test@example.com", "password": "password123"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json())

if __name__ == "__main__":
    unittest.main()