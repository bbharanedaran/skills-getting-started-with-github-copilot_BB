"""Pytest configuration and shared fixtures for API tests using AAA pattern.

This module provides:
- TestClient fixture for FastAPI application
- Activities data reset fixture to ensure test isolation
- Helper functions for common assertions
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


DEFAULT_ACTIVITIES = {
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
    "Basketball Team": {
        "description": "Practice and compete in basketball games",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
        "max_participants": 15,
        "participants": []
    },
    "Soccer Club": {
        "description": "Train and play soccer matches",
        "schedule": "Wednesdays and Saturdays, 3:00 PM - 5:00 PM",
        "max_participants": 22,
        "participants": []
    },
    "Art Club": {
        "description": "Explore various art forms and create masterpieces",
        "schedule": "Mondays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": []
    },
    "Drama Club": {
        "description": "Act in plays and improve theatrical skills",
        "schedule": "Fridays, 4:00 PM - 6:00 PM",
        "max_participants": 20,
        "participants": []
    },
    "Debate Club": {
        "description": "Engage in debates and develop critical thinking",
        "schedule": "Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 16,
        "participants": []
    },
    "Science Club": {
        "description": "Conduct experiments and learn about science",
        "schedule": "Mondays and Wednesdays, 3:00 PM - 4:00 PM",
        "max_participants": 25,
        "participants": []
    }
}


@pytest.fixture
def client():
    """Provide a FastAPI TestClient for making HTTP requests to the app.
    
    This fixture is used in the Arrange phase of AAA tests.
    """
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to default state before each test.
    
    This fixture ensures test isolation by resetting in-memory data to known state.
    Used in the Arrange phase of AAA tests.
    
    Yields:
        None. After yield, fixture restores original data.
    """
    # Store original state
    original_activities = dict(activities)
    
    # Clear and reset to defaults
    activities.clear()
    activities.update(DEFAULT_ACTIVITIES)
    
    yield
    
    # Restore original state after test
    activities.clear()
    activities.update(original_activities)
