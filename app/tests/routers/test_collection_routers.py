import pytest
from fastapi.testclient import TestClient

from app.infra.auth import get_user
from app.main import create_application
from app.presentation.schemas.collection_schemas import CreateCollectionResponse


@pytest.fixture
def client():
    app = create_application()
    app.dependency_overrides[get_user] = lambda: "test-user-id"
    return TestClient(app)


def test_add_collection_success(client, mocker):
    mock_controller = mocker.Mock()
    mock_controller.create_collection.return_value = CreateCollectionResponse(
        collection_id="col123",
        collection_name="Test Collection",
    )

    mocker.patch(
        "app.presentation.routers.collection_routers.get_collection_controller",
        return_value=mock_controller,
    )

    response = client.post(
        "/add-collection",
        json={
            "collection_name": "Test Collection",
            "database_id": "db1",
            "embedding_model_id": "model1",
        },
    )

    assert response.status_code == 200
    assert response.json()["collection_id"] == "col123"


def test_list_collections_success(client, mocker):
    mock_controller = mocker.Mock()
    mock_controller.list_collections.return_value = [
        {
            "id": "col1",
            "user_id": "user1",
            "name": "My Collection",
            "created_at": "2025-07-28T00:00:00Z",
        }
    ]

    mocker.patch(
        "app.presentation.routers.collection_routers.get_collection_controller",
        return_value=mock_controller,
    )

    response = client.get("/list-collections")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["id"] == "col1"


def test_delete_collection_success(client, mocker):
    mock_controller = mocker.Mock()
    mock_controller.delete_collection.return_value = {"message": "deleted"}

    mocker.patch(
        "app.presentation.routers.collection_routers.get_collection_controller",
        return_value=mock_controller,
    )

    response = client.delete("/delete-collection/col1")

    assert response.status_code == 200
    assert response.json()["message"] == "deleted"
