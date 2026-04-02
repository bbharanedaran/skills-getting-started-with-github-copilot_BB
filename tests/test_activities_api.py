"""API tests for Mergington High School Activities endpoints using AAA pattern.

This module implements the Arrange-Act-Assert (AAA) testing pattern for all
API endpoints. Each test clearly separates:
- Arrange: Set up test data and fixtures
- Act: Execute the API call being tested
- Assert: Verify expected outcomes
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint using AAA pattern."""

    def test_retrieve_all_activities_successfully(self, client, reset_activities):
        """Test retrieving all activities from the API.
        
        AAA Pattern:
        - Arrange: TestClient is ready, activities reset to default state
        - Act: Make GET request to /activities endpoint
        - Assert: Verify 200 status, correct data structure, all 9 activities returned
        """
        # Arrange
        # (setup is handled by fixtures: client and reset_activities)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities_data = response.json()
        assert len(activities_data) == 9
        assert "Chess Club" in activities_data
        assert "Programming Class" in activities_data
        assert "Gym Class" in activities_data
        assert "Basketball Team" in activities_data
        assert "Soccer Club" in activities_data

    def test_activities_contain_correct_data_structure(self, client, reset_activities):
        """Test that returned activities have the correct data structure.
        
        AAA Pattern:
        - Arrange: Expected schema is defined
        - Act: Fetch all activities via GET /activities
        - Assert: Verify each activity has required fields with correct types
        """
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert
        for activity_name, activity in activities_data.items():
            assert isinstance(activity_name, str)
            assert set(activity.keys()) == required_fields
            assert isinstance(activity["description"], str)
            assert isinstance(activity["schedule"], str)
            assert isinstance(activity["max_participants"], int)
            assert isinstance(activity["participants"], list)
            assert all(isinstance(email, str) for email in activity["participants"])

    def test_activities_have_correct_participant_counts(self, client, reset_activities):
        """Test that participant counts match expected values.
        
        AAA Pattern:
        - Arrange: Known expected participant counts
        - Act: Get activities and extract participant data
        - Assert: Verify participant counts match expectations
        """
        # Arrange
        expected_counts = {
            "Chess Club": 2,
            "Programming Class": 2,
            "Gym Class": 2,
            "Basketball Team": 0,
            "Soccer Club": 0
        }
        
        # Act
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert
        for activity_name, expected_count in expected_counts.items():
            assert len(activities_data[activity_name]["participants"]) == expected_count


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint using AAA pattern."""

    def test_successful_signup(self, client, reset_activities):
        """Test successfully signing up a new student for an activity.
        
        AAA Pattern:
        - Arrange: Initialize activity state, prepare valid email
        - Act: POST signup request with valid activity and email
        - Assert: Verify 200 response, email added to participants, confirmation message
        """
        # Arrange
        activity_name = "Chess Club"
        new_email = "newstudent@mergington.edu"
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={new_email}"
        )
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert new_email in result["message"]
        assert activity_name in result["message"]
        
        # Verify participant was actually added
        activities_response = client.get("/activities")
        new_count = len(activities_response.json()[activity_name]["participants"])
        assert new_count == initial_count + 1
        assert new_email in activities_response.json()[activity_name]["participants"]

    def test_signup_with_invalid_activity_name(self, client, reset_activities):
        """Test signup attempt with non-existent activity.
        
        AAA Pattern:
        - Arrange: Have a non-existent activity name ready
        - Act: Attempt POST signup with invalid activity name
        - Assert: Verify 404 response with appropriate error detail
        """
        # Arrange
        invalid_activity = "Nonexistent Activity"
        valid_email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup?email={valid_email}"
        )
        
        # Assert
        assert response.status_code == 404
        error_detail = response.json()
        assert "detail" in error_detail
        assert "Activity not found" in error_detail["detail"]

    def test_signup_duplicate_student(self, client, reset_activities):
        """Test duplicate signup: same student tries to enroll twice in same activity.
        
        AAA Pattern:
        - Arrange: Have a student already enrolled in an activity
        - Act: Attempt to sign up the same student again
        - Assert: Verify 400 error and "already signed up" message (prevents duplicates)
        """
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"
        
        # Act - Attempt duplicate signup (student already enrolled)
        response = client.post(
            f"/activities/{activity_name}/signup?email={existing_email}"
        )
        
        # Assert - Verify duplicate signup is prevented
        assert response.status_code == 400
        error_detail = response.json()
        assert "detail" in error_detail
        assert "already signed up" in error_detail["detail"]

    def test_signup_multiple_students_same_activity(self, client, reset_activities):
        """Test multiple different students signing up for the same activity.
        
        AAA Pattern:
        - Arrange: Multiple unique student emails ready
        - Act: Sign up each student sequentially
        - Assert: Verify all students are added to participants list
        """
        # Arrange
        activity_name = "Programming Class"
        new_students = ["alice@mergington.edu", "bob@mergington.edu", "charlie@mergington.edu"]
        initial_count = 2  # Emma and Sophia already enrolled
        
        # Act
        for email in new_students:
            response = client.post(
                f"/activities/{activity_name}/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Assert
        activities_response = client.get("/activities")
        final_participants = activities_response.json()[activity_name]["participants"]
        assert len(final_participants) == initial_count + len(new_students)
        for email in new_students:
            assert email in final_participants

    def test_signup_with_special_characters_in_email(self, client, reset_activities):
        """Test signup with email containing special characters that need URL encoding.
        
        AAA Pattern:
        - Arrange: Email with special characters (underscore) ready
        - Act: POST signup with special character email
        - Assert: Verify signup succeeds and email is stored correctly
        """
        # Arrange
        activity_name = "Gym Class"
        # Using underscore as a safe special character that survives URL query encoding
        special_email = "student_nickname@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={special_email}"
        )
        
        # Assert
        assert response.status_code == 200
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity_name]["participants"]
        assert special_email in participants

    def test_signup_response_message_format(self, client, reset_activities):
        """Test that signup response message has correct format.
        
        AAA Pattern:
        - Arrange: Prepare test data
        - Act: Execute signup
        - Assert: Verify response message format contains email and activity
        """
        # Arrange
        activity_name = "Chess Club"
        email = "format_test@mergington.edu"
        expected_text_patterns = [email, activity_name]
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        result = response.json()
        
        # Assert
        assert response.status_code == 200
        message = result["message"]
        for pattern in expected_text_patterns:
            assert pattern in message

    def test_signup_missing_email_parameter(self, client, reset_activities):
        """Test signup attempt without email parameter.
        
        AAA Pattern:
        - Arrange: Activity name ready, email parameter omitted
        - Act: Attempt POST signup without email query parameter
        - Assert: Verify appropriate error response
        """
        # Arrange
        activity_name = "Chess Club"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup")
        
        # Assert
        # FastAPI will return 422 Unprocessable Entity for missing required param
        assert response.status_code == 422


class TestActivityDataIntegrity:
    """Tests for data integrity and consistency across operations."""

    def test_original_activities_preserved_after_signup(self, client, reset_activities):
        """Test that signup operations don't modify activity metadata.
        
        AAA Pattern:
        - Arrange: Get original activity details
        - Act: Sign up a student
        - Assert: Verify activity description, schedule, max_participants unchanged
        """
        # Arrange
        activity_name = "Chess Club"
        original_response = client.get("/activities")
        original_activity = original_response.json()[activity_name]
        original_desc = original_activity["description"]
        original_schedule = original_activity["schedule"]
        original_max = original_activity["max_participants"]
        
        # Act
        client.post(f"/activities/{activity_name}/signup?email=test@mergington.edu")
        
        # Assert
        updated_response = client.get("/activities")
        updated_activity = updated_response.json()[activity_name]
        assert updated_activity["description"] == original_desc
        assert updated_activity["schedule"] == original_schedule
        assert updated_activity["max_participants"] == original_max
        # Only participants should change
        assert len(updated_activity["participants"]) == len(original_activity["participants"]) + 1

    def test_signup_doesnt_affect_other_activities(self, client, reset_activities):
        """Test that signing up for one activity doesn't affect others.
        
        AAA Pattern:
        - Arrange: Get original state of all activities
        - Act: Sign up for one specific activity
        - Assert: Verify other activities remain unchanged
        """
        # Arrange
        target_activity = "Chess Club"
        other_activities = ["Programming Class", "Gym Class"]
        
        original_response = client.get("/activities")
        original_state = {
            name: dict(activity) for name, activity in original_response.json().items()
        }
        
        # Act
        client.post(f"/activities/{target_activity}/signup?email=new@mergington.edu")
        
        # Assert
        updated_response = client.get("/activities")
        updated_state = updated_response.json()
        
        for other_activity in other_activities:
            assert (len(updated_state[other_activity]["participants"]) == 
                   len(original_state[other_activity]["participants"]))
