import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base
from app.models import Feedback

# Create a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_feedback.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test database tables
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


class TestFeedbackEndpoint:
    """Test cases for the feedback endpoint."""
    
    def setup_method(self):
        """Set up before each test method."""
        # Clear feedback table
        db = TestingSessionLocal()
        db.query(Feedback).delete()
        db.commit()
        db.close()
    
    def test_submit_feedback_success(self):
        """Test successful feedback submission."""
        feedback_data = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "message": "This is a great application! I love the urban green space features."
        }
        
        response = client.post("/feedback", json=feedback_data)
        
        assert response.status_code == 201
        response_data = response.json()
        assert "message" in response_data
        assert "feedback_id" in response_data
        assert response_data["message"] == "Thank you for your feedback! We appreciate your input."
        assert isinstance(response_data["feedback_id"], int)
        
        # Verify feedback was saved to database
        db = TestingSessionLocal()
        feedback = db.query(Feedback).filter(Feedback.id == response_data["feedback_id"]).first()
        assert feedback is not None
        assert feedback.name == "John Doe"
        assert feedback.email == "john.doe@example.com"
        assert feedback.message == "This is a great application! I love the urban green space features."
        assert feedback.created_at is not None
        assert feedback.updated_at is not None
        db.close()
    
    def test_submit_feedback_missing_name(self):
        """Test feedback submission with missing name."""
        feedback_data = {
            "email": "john.doe@example.com",
            "message": "This is a great application!"
        }
        
        response = client.post("/feedback", json=feedback_data)
        assert response.status_code == 422
    
    def test_submit_feedback_empty_name(self):
        """Test feedback submission with empty name."""
        feedback_data = {
            "name": "",
            "email": "john.doe@example.com",
            "message": "This is a great application!"
        }
        
        response = client.post("/feedback", json=feedback_data)
        assert response.status_code == 422
    
    def test_submit_feedback_name_too_long(self):
        """Test feedback submission with name too long."""
        feedback_data = {
            "name": "a" * 101,  # 101 characters, exceeds 100 max
            "email": "john.doe@example.com",
            "message": "This is a great application!"
        }
        
        response = client.post("/feedback", json=feedback_data)
        assert response.status_code == 422
    
    def test_submit_feedback_invalid_email(self):
        """Test feedback submission with invalid email."""
        feedback_data = {
            "name": "John Doe",
            "email": "invalid-email",
            "message": "This is a great application!"
        }
        
        response = client.post("/feedback", json=feedback_data)
        assert response.status_code == 422
    
    def test_submit_feedback_missing_email(self):
        """Test feedback submission with missing email."""
        feedback_data = {
            "name": "John Doe",
            "message": "This is a great application!"
        }
        
        response = client.post("/feedback", json=feedback_data)
        assert response.status_code == 422
    
    def test_submit_feedback_message_too_short(self):
        """Test feedback submission with message too short."""
        feedback_data = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "message": "Short"  # Less than 10 characters
        }
        
        response = client.post("/feedback", json=feedback_data)
        assert response.status_code == 422
    
    def test_submit_feedback_message_too_long(self):
        """Test feedback submission with message too long."""
        feedback_data = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "message": "a" * 1001  # 1001 characters, exceeds 1000 max
        }
        
        response = client.post("/feedback", json=feedback_data)
        assert response.status_code == 422
    
    def test_submit_feedback_missing_message(self):
        """Test feedback submission with missing message."""
        feedback_data = {
            "name": "John Doe",
            "email": "john.doe@example.com"
        }
        
        response = client.post("/feedback", json=feedback_data)
        assert response.status_code == 422
    
    def test_submit_feedback_special_characters(self):
        """Test feedback submission with special characters."""
        feedback_data = {
            "name": "José García-López",
            "email": "jose.garcia@example.com",
            "message": "¡Excelente aplicación! Me encanta cómo funciona con espacios verdes. 🌳🏞️"
        }
        
        response = client.post("/feedback", json=feedback_data)
        assert response.status_code == 201
        
        response_data = response.json()
        assert "feedback_id" in response_data
        
        # Verify special characters were preserved
        db = TestingSessionLocal()
        feedback = db.query(Feedback).filter(Feedback.id == response_data["feedback_id"]).first()
        assert feedback.name == "José García-López"
        assert feedback.message == "¡Excelente aplicación! Me encanta cómo funciona con espacios verdes. 🌳🏞️"
        db.close()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])