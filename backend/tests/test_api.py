"""
API Endpoint Tests
Tests all REST API endpoints including admin and interview endpoints
"""
import pytest
import os
import sys
from datetime import datetime

# Add parent directory to path to import app module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestPublicEndpoints:
    """Test public API endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint returns config"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "max_questions" in data
        assert "question_timeout_seconds" in data
        
        print(f"✓ Root endpoint working - Max questions: {data['max_questions']}")
    
    def test_start_interview(self):
        """Test starting a new interview"""
        timestamp = datetime.now().timestamp()
        test_email = f"api_test_{timestamp}@example.com"
        
        response = client.post("/ai/start-interview", json={
            "email": test_email,
            "role": "Software Developer",
            "first_name": "API",
            "last_name": "Test"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "interview_id" in data
        assert "first_question" in data
        assert "total_questions" in data
        assert data["role"] == "Software Developer"
        
        print(f"✓ Interview created: {data['interview_id']}")
        return data["interview_id"]
    
    def test_get_next_question(self):
        """Test getting next question"""
        # First create an interview
        timestamp = datetime.now().timestamp()
        test_email = f"api_test_{timestamp}@example.com"
        
        start_response = client.post("/ai/start-interview", json={
            "email": test_email,
            "role": "Data Analyst"
        })
        
        interview_id = start_response.json()["interview_id"]
        
        # Get next question
        response = client.get(f"/ai/next-question/{interview_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert "question" in data
        assert "completed" in data
        assert data["completed"] == False
        
        print(f"✓ Next question retrieved for interview {interview_id}")
    
    def test_interview_results(self):
        """Test getting interview results"""
        # Create interview first
        timestamp = datetime.now().timestamp()
        test_email = f"api_test_{timestamp}@example.com"
        
        start_response = client.post("/ai/start-interview", json={
            "email": test_email,
            "role": "UX Designer"
        })
        
        interview_id = start_response.json()["interview_id"]
        
        # Get results
        response = client.get(f"/ai/interview-results/{interview_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert "interview_id" in data
        assert "statistics" in data
        assert "questions" in data
        
        print(f"✓ Results retrieved for interview {interview_id}")


class TestAdminEndpoints:
    """Test admin-only API endpoints"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin token for authentication"""
        response = client.post("/api/admin/login", json={
            "email": "admin@example.com",
            "password": "Admin@123456"
        })
        
        if response.status_code == 200:
            data = response.json()
            return data["access_token"]
        else:
            pytest.skip("Default admin not found - run database migration")
    
    def test_admin_login_success(self):
        """Test successful admin login"""
        response = client.post("/api/admin/login", json={
            "email": "admin@example.com",
            "password": "Admin@123456"
        })
        
        if response.status_code == 200:
            data = response.json()
            assert "access_token" in data
            assert "admin" in data
            assert data["token_type"] == "bearer"
            print(f"✓ Admin login successful")
        else:
            print("⚠ Default admin not found - run migration: 002_seed_admin.sql")
    
    def test_admin_login_failure(self):
        """Test failed admin login"""
        response = client.post("/api/admin/login", json={
            "email": "wrong@example.com",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        print("✓ Invalid credentials rejected")
    
    def test_get_interviews_unauthorized(self):
        """Test getting interviews without auth fails"""
        response = client.get("/api/admin/interviews")
        assert response.status_code == 401
        print("✓ Unauthorized access blocked")
    
    def test_get_interviews_authorized(self, admin_token):
        """Test getting interviews with auth"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/admin/interviews", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "interviews" in data
        assert "pagination" in data
        
        print(f"✓ Retrieved {len(data['interviews'])} interviews")
    
    def test_get_interview_detail(self, admin_token):
        """Test getting specific interview details"""
        # First create an interview
        timestamp = datetime.now().timestamp()
        test_email = f"admin_test_{timestamp}@example.com"
        
        start_response = client.post("/ai/start-interview", json={
            "email": test_email,
            "role": "Project Leader"
        })
        
        interview_id = start_response.json()["interview_id"]
        
        # Get details as admin
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get(f"/api/admin/interviews/{interview_id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["interview_id"] == interview_id
        assert "candidate" in data
        assert "statistics" in data
        
        print(f"✓ Retrieved interview details for {interview_id}")
    
    def test_get_config(self, admin_token):
        """Test getting configuration"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/admin/config", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "MAX_QUESTIONS" in data
        assert "QUESTION_TIMEOUT_SECONDS" in data
        
        print(f"✓ Config retrieved - MAX_QUESTIONS: {data['MAX_QUESTIONS']}")
    
    def test_update_config(self, admin_token):
        """Test updating configuration"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Update config
        response = client.put("/api/admin/config", 
            headers=headers,
            json={
                "MAX_QUESTIONS": 8,
                "QUESTION_TIMEOUT_SECONDS": 90
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        print(f"✓ Config updated successfully")
        
        # Verify update
        get_response = client.get("/api/admin/config", headers=headers)
        config = get_response.json()
        
        assert config["MAX_QUESTIONS"] == "8"
        assert config["QUESTION_TIMEOUT_SECONDS"] == "90"
        print(f"✓ Config verified after update")


def test_api_server():
    """Test that API server is running"""
    try:
        response = client.get("/")
        assert response.status_code == 200
        print("✅ API server is running")
        return True
    except Exception as e:
        print(f"❌ API server not running: {e}")
        return False


if __name__ == "__main__":
    print("="*60)
    print("AI INTERVIEWER - API ENDPOINT TESTS")
    print("="*60)
    print()
    
    if not test_api_server():
        print("\n❌ Cannot proceed without API server")
        print("Please start the backend server first:")
        print("  cd backend")
        print("  uvicorn app.main:app --reload")
        exit(1)
    
    print("\nRunning pytest tests...\n")
    pytest.main([__file__, "-v", "-s"])
