import pytest
from fastapi.testclient import TestClient

from app.infra.auth import get_user
from app.main import create_application


@pytest.fixture
def client():
    app = create_application()
    app.dependency_overrides[get_user] = lambda: "test-user-id"
    return TestClient(app)


@pytest.mark.parametrize(
    "endpoint, payload",
    [
        (
            "/scan",
            {
                "data_source_id": "myorg",
            },
        ),
    ],
)
def test_scan_endpoints_success(client, mocker, endpoint, payload):
    from app.deps import get_task_service

    # Mock the task service
    mock_task_service = mocker.Mock()

    # Override the dependency in the app
    client.app.dependency_overrides[get_task_service] = lambda: mock_task_service

    # Mock the background task function
    mock_run_scan_task = mocker.patch(
        "app.presentation.routers.scanning_routers.run_scan_task"
    )

    response = client.post(endpoint, json=payload)

    assert response.status_code == 202
    assert "task_id" in response.json()

    # Verify task service methods were called
    mock_task_service.create.assert_called_once()
    mock_task_service.progress.assert_called_once_with(mocker.ANY, 1)
