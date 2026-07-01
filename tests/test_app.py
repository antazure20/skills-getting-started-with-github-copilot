import copy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture(autouse=True)
def restore_activities_state():
    original_activities = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original_activities))


@pytest.fixture
def client():
    with TestClient(app_module.app) as test_client:
        yield test_client


def test_list_activities_returns_activity_catalog(client):
    # Arrange
    expected_activity_names = {"Chess Club", "Programming Class", "Gym Class"}

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert expected_activity_names.issubset(payload.keys())
    assert payload["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_for_activity_adds_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    original_participants = list(app_module.activities[activity_name]["participants"])

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert app_module.activities[activity_name]["participants"] == original_participants + [email]


def test_duplicate_signup_returns_error_without_adding_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    original_participants = list(app_module.activities[activity_name]["participants"])

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert app_module.activities[activity_name]["participants"] == original_participants


def test_unregister_participant_removes_email_from_activity(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    original_participants = list(app_module.activities[activity_name]["participants"])

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert app_module.activities[activity_name]["participants"] == [
        participant for participant in original_participants if participant != email
    ]
