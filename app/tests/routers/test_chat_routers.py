import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from app.infra.auth import get_user
from app.main import create_application
from app.presentation.schemas.chat_schemas import (
    AddChatMetadataResponse,
    DeleteChatMetadataResponse,
)


@pytest.fixture
def client(mocker):
    app = create_application()

    # Override user authentication
    app.dependency_overrides[get_user] = lambda: "test-user-id"

    # Patch underlying infrastructure
    mocker.patch(
        "app.presentation.routers.chat_routers.get_vector_store",
        return_value=MagicMock(),
    )
    mocker.patch(
        "app.presentation.routers.chat_routers.get_chat_store",
        return_value=MagicMock(),
    )

    return TestClient(app)


def test_chat_success(client, mocker):
    mock_controller = MagicMock()
    mock_controller.chat.return_value = {"message": "Hello!"}
    mocker.patch(
        "app.presentation.routers.chat_routers.get_chat_controller",
        return_value=mock_controller,
    )

    response = client.post(
        "/chat",
        json={
            "chat_id": "chat1",
            "message": "Hi",
            "system_prompt": "",
            "token_limit": 4096,
        },
    )

    assert response.status_code == 202
    assert response.json() == {"message": "Hello!"}
    mock_controller.chat.assert_called_once()


def test_stream_chat_success(client, mocker):
    mock_controller = MagicMock()
    mock_controller.stream_chat.return_value = iter(
        ["stream line 1\n", "stream line 2\n"]
    )
    mocker.patch(
        "app.presentation.routers.chat_routers.get_chat_controller",
        return_value=mock_controller,
    )

    response = client.post(
        "/stream-chat",
        json={
            "chat_id": "chat1",
            "message": "Hi",
            "system_prompt": "",
            "token_limit": 4096,
        },
    )

    assert response.status_code == 200
    assert b"stream line" in response.content
    mock_controller.stream_chat.assert_called_once()


def test_add_chat_success(client, mocker):
    mock_controller = MagicMock()
    mock_controller.add_chat.return_value = AddChatMetadataResponse(chat_id="chat1")
    mocker.patch(
        "app.presentation.routers.chat_routers.get_chat_controller",
        return_value=mock_controller,
    )

    response = client.post(
        "/add-chat",
        json={
            "collection_id": "col1",
            "chat_name": "Test Chat",
            "database_id": "db1",
            "model_id": "model-xyz",
            "chat_source": "web",
            "prompt_id": "default",
        },
    )

    assert response.status_code == 200
    assert response.json() == {"chat_id": "chat1"}
    mock_controller.add_chat.assert_called_once()


def test_delete_chat_success(client, mocker):
    mock_controller = MagicMock()
    mock_controller.delete_chat.return_value = DeleteChatMetadataResponse(
        message="Chat deleted successfully"
    )
    mocker.patch(
        "app.presentation.routers.chat_routers.get_chat_controller",
        return_value=mock_controller,
    )

    response = client.delete("/delete-chat/chat1")

    assert response.status_code == 200
    assert response.json() == {"message": "Chat deleted successfully"}
    mock_controller.delete_chat.assert_called_once()


def test_fetch_chats_success(client, mocker):
    mocker.patch(
        "app.presentation.routers.chat_routers.fetch_items",
        return_value=[
            {
                "id": "chat1",
                "name": "Test Chat",
                "created_at": "2025-07-28T12:00:00Z",
                "collection_id": "col1",
                "model_id": "model1",
                "chat_source": "web",
                "prompt_id": "default",
            }
        ],
    )

    response = client.get("/list-chats")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert response.json()[0]["name"] == "Test Chat"
    assert response.json()[0]["collection_id"] == "col1"
    assert response.json()[0]["model_id"] == "model1"


def test_fetch_chats_not_found(client, mocker):
    mocker.patch("app.presentation.routers.chat_routers.fetch_items", return_value=[])

    response = client.get("/list-chats")

    assert response.status_code == 404
    assert response.json()["detail"] == "404: No chats found for the user"


def test_get_chat_history_success(client, mocker):
    mock_controller = MagicMock()
    mock_controller.get_chat_history.return_value = [
        {"role": "user", "message": "Hello"},
        {"role": "assistant", "message": "Hi!"},
    ]
    mocker.patch(
        "app.presentation.routers.chat_routers.get_chat_controller",
        return_value=mock_controller,
    )

    response = client.post("/get-chat-history", json={"chat_id": "chat1"})

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert response.json()[0]["role"] == "user"
    mock_controller.get_chat_history.assert_called_once()


def test_get_chat_history_not_found(client, mocker):
    mock_controller = MagicMock()
    mock_controller.get_chat_history.return_value = []
    mocker.patch(
        "app.presentation.routers.chat_routers.get_chat_controller",
        return_value=mock_controller,
    )

    response = client.post("/get-chat-history", json={"chat_id": "chat1"})

    assert response.status_code == 200
    assert response.json() == []
