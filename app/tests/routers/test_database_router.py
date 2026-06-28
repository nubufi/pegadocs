import pytest
from fastapi.testclient import TestClient
from app.main import create_application
from app.infra.auth import get_user


@pytest.fixture
def client():
    app = create_application()

    # Mock user authentication
    app.dependency_overrides[get_user] = lambda: "test-user-id"

    return TestClient(app)


def test_create_database_index_success(client, mocker):
    mock_create = mocker.patch(
        "app.presentation.controllers.database_controller.DataBaseController.create_database_index"
    )
    mock_create.return_value.model_dump.return_value = {"id": "db-123"}

    response = client.post(
        "/create-database-index",
        json={
            "name": "my-db",
            "type": "postgres",
            "config": {"host": "localhost", "port": 5432},
            "storage_type": "vector",
        },
    )

    assert response.status_code == 200
    assert response.json() == {"id": "db-123"}


def test_list_database_indexes_success(client, mocker):
    mock_list = mocker.patch(
        "app.presentation.controllers.database_controller.DataBaseController.list_database_indexes"
    )

    mock_list.return_value = [
        mocker.Mock(
            model_dump=lambda: {
                "id": "db-1",
                "name": "my-db",
                "type": "postgres",
                "config": {"host": "localhost"},
                "storage_type": "vector",
                "created_at": "2025-07-28T12:00:00",
                "is_default": False,
            }
        )
    ]

    response = client.get("/list-database-indexes")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["id"] == "db-1"


def test_delete_database_index_success(client, mocker):
    mock_delete = mocker.patch(
        "app.presentation.controllers.database_controller.DataBaseController.delete_database_index"
    )

    response = client.delete("/delete-database-index/db-123")

    assert response.status_code == 204
    assert response.content == b"null"
