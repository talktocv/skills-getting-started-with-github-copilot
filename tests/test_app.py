"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    from app import activities
    
    # Store original state
    original_state = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball": {
            "description": "Team-based basketball games and training",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": []
        },
        "Tennis": {
            "description": "Individual and doubles tennis matches",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:00 PM",
            "max_participants": 12,
            "participants": []
        },
        "Drama Club": {
            "description": "Theater performances and acting workshops",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": []
        },
        "Art Class": {
            "description": "Painting, drawing, and sculpture techniques",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": []
        },
        "Debate Team": {
            "description": "Competitive debate and public speaking",
            "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": []
        },
        "Science Club": {
            "description": "Hands-on science experiments and research",
            "schedule": "Fridays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": []
        }
    }
    
    # Clear and reset
    activities.clear()
    activities.update(original_state)
    
    yield
    
    # Restore after test
    activities.clear()
    activities.update(original_state)


class TestGetActivities:
    """Tests for the GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all available activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Basketball" in data
        assert len(data) == 9
    
    def test_activity_has_required_fields(self, client, reset_activities):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
    
    def test_participants_list_is_array(self, client, reset_activities):
        """Test that participants field is an array"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_data in data.values():
            assert isinstance(activity_data["participants"], list)


class TestSignup:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_successful_signup(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Basketball/signup?email=test@mergington.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "test@mergington.edu" in data["message"]
        assert "Basketball" in data["message"]
    
    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup actually adds the participant"""
        client.post("/activities/Basketball/signup?email=test@mergington.edu")
        
        response = client.get("/activities")
        activities = response.json()
        assert "test@mergington.edu" in activities["Basketball"]["participants"]
    
    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signup for non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent/signup?email=test@mergington.edu"
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_duplicate_signup_fails(self, client, reset_activities):
        """Test that duplicate signup returns 400"""
        # Michael is already signed up for Chess Club
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()
    
    def test_signup_different_activities(self, client, reset_activities):
        """Test signing up for multiple different activities"""
        email = "multi@mergington.edu"
        
        response1 = client.post(
            f"/activities/Basketball/signup?email={email}"
        )
        response2 = client.post(
            f"/activities/Tennis/signup?email={email}"
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        activities = client.get("/activities").json()
        assert email in activities["Basketball"]["participants"]
        assert email in activities["Tennis"]["participants"]


class TestUnregister:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_successful_unregister(self, client, reset_activities):
        """Test successful unregister from an activity"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes the participant"""
        client.delete(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        
        response = client.get("/activities")
        activities = response.json()
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test unregister for non-existent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent/unregister?email=test@mergington.edu"
        )
        
        assert response.status_code == 404
    
    def test_unregister_not_registered_student(self, client, reset_activities):
        """Test unregister for student not registered returns 400"""
        response = client.delete(
            "/activities/Basketball/unregister?email=notregistered@mergington.edu"
        )
        
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"].lower()
    
    def test_signup_and_unregister_flow(self, client, reset_activities):
        """Test full flow of signup then unregister"""
        email = "flow@mergington.edu"
        
        # Sign up
        signup_response = client.post(
            f"/activities/Basketball/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Verify signup
        activities = client.get("/activities").json()
        assert email in activities["Basketball"]["participants"]
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/Basketball/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        
        # Verify unregister
        activities = client.get("/activities").json()
        assert email not in activities["Basketball"]["participants"]


class TestRoot:
    """Tests for the root endpoint"""
    
    def test_root_redirect(self, client):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
