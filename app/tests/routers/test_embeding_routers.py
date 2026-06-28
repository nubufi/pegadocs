import pytest
from fastapi.testclient import TestClient

from app.infra.auth import get_user
from app.main import create_application


@pytest.fixture
def client():
    app = create_application()
    app.dependency_overrides[get_user] = lambda: "test-user-id"
    return TestClient(app)


def test_get_task_status_success(client, mocker):
    from app.application.protocols.task_store import TaskStatus
    from app.deps import get_task_service
    from types import SimpleNamespace

    # Mock the task service status method
    mock_task_service = mocker.Mock()
    mock_task_service.status.return_value = {
        "status": TaskStatus.DONE,
        "result": {"summary": "done"},
    }

    # Override the dependency in the app
    client.app.dependency_overrides[get_task_service] = lambda: mock_task_service

    mock_summary = SimpleNamespace(
        ready=False,
        pending_documents={},
        progress_percent=0,
        data_source_id=None,
        total_tokens=0,
    )
    mocker.patch(
        "app.presentation.routers.embedding_routers._job_monitor.load_summary",
        return_value=mock_summary,
    )

    response = client.get("/embed/fake-task-id")
    assert response.status_code == 200
    assert response.json()["status"] == "DONE"
    assert "result" in response.json()


@pytest.mark.parametrize(
    "endpoint, payload",
    [
        (
            "/embed",
            {
                "data_source_id": "ds1",
                "collection_id": "col1",
            },
        ),
    ],
)
def test_embed_sources_success(client, mocker, endpoint, payload):
    from app.deps import get_task_service

    # Mock the task service to avoid Redis dependency
    mock_task_service = mocker.Mock()
    mock_task_service.create.return_value = None
    mock_task_service.progress.return_value = None

    mock_delay = mocker.patch(
        "app.tasks.embedding.run_embed_task.delay",
        return_value=None,
    )

    client.app.dependency_overrides[get_task_service] = lambda: mock_task_service

    response = client.post(endpoint, json=payload)
    assert response.status_code == 202
    mock_delay.assert_called_once()
