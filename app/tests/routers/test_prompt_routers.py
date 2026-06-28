import pytest
from fastapi.testclient import TestClient
from app.main import create_application
from app.infra.auth import get_user


@pytest.fixture
def client():
    app = create_application()
    app.dependency_overrides[get_user] = lambda: "test-user-id"
    return TestClient(app)


def test_create_prompt_success(client, mocker):
    mock_create = mocker.patch(
        "app.presentation.controllers.prompt_controller.PromptController.create_prompt"
    )
    mock_create.return_value.model_dump.return_value = {"id": "prompt-123"}

    response = client.post(
        "/create-prompt",
        json={
            "name": "MyPrompt",
            "prompt": "This is a prompt",
        },
    )

    assert response.status_code == 200
    assert response.json() == {"id": "prompt-123"}


def test_list_prompts_success(client, mocker):
    mock_list = mocker.patch(
        "app.presentation.controllers.prompt_controller.PromptController.list_prompts"
    )

    mock_list.return_value = [
        mocker.Mock(
            model_dump=lambda: {
                "id": "model-1",
                "name": "Prompt A",
                "prompt": "This is a prompt A",
            }
        ),
        mocker.Mock(
            model_dump=lambda: {
                "id": "model-2",
                "name": "Prompt B",
                "prompt": "This is a prompt B",
            }
        ),
    ]

    response = client.get("/list-prompts")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["name"] == "Prompt A"


def test_delete_prompt_success(client, mocker):
    mock_delete = mocker.patch(
        "app.presentation.controllers.prompt_controller.PromptController.delete_prompt"
    )

    response = client.delete("/delete-prompt/prompt-1")

    assert response.status_code == 204
    assert response.content == b"null"
