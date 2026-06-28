import pytest
from fastapi.testclient import TestClient
from app.main import create_application
from app.infra.auth import get_user


@pytest.fixture
def client():
    app = create_application()
    app.dependency_overrides[get_user] = lambda: "test-user-id"
    return TestClient(app)


def test_create_model_success(client, mocker):
    mock_create = mocker.patch(
        "app.presentation.controllers.model_controller.ModelController.create_model"
    )
    mock_create.return_value.model_dump.return_value = {"id": "model-123"}

    response = client.post(
        "/create-model",
        json={
            "name": "MyModel",
            "type": "embedding",
            "provider": "azure_openai",
            "dimensions": 1536,
            "config": {},
        },
    )

    assert response.status_code == 200
    assert response.json() == {"id": "model-123"}


def test_list_models_success(client, mocker):
    mock_list = mocker.patch(
        "app.presentation.controllers.model_controller.ModelController.list_models"
    )

    mock_list.return_value = [
        mocker.Mock(
            model_dump=lambda: {
                "id": "model-1",
                "name": "Model A",
                "provider": "openai",
                "type": "embedding",
                "dimensions": 1536,
                "config": {},
                "is_default": False,
            }
        ),
        mocker.Mock(
            model_dump=lambda: {
                "id": "model-2",
                "name": "Model B",
                "provider": "openai",
                "type": "chat",
                "dimensions": 0,
                "config": {},
                "is_default": True,
            }
        ),
    ]

    response = client.get("/list-models")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["name"] == "Model A"
    assert data[1]["is_default"] is True


def test_delete_model_success(client, mocker):
    mock_delete = mocker.patch(
        "app.presentation.controllers.model_controller.ModelController.delete_model"
    )

    response = client.delete("/delete-model/model-1")

    assert response.status_code == 204
    assert response.content == b"null"
