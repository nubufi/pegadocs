import pytest
from fastapi.testclient import TestClient

from app.infra.config import settings
from app.main import create_application


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(settings, "ENABLE_MOCK_API", True)
    return TestClient(create_application())


@pytest.fixture
def auth_headers(client):
    response = client.post(
        "/mock/auth/login",
        json={"email": "demo@pegadocs.local", "password": "demo1234"},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_mock_api_is_disabled_by_default(monkeypatch):
    monkeypatch.setattr(settings, "ENABLE_MOCK_API", False)
    response = TestClient(create_application()).post(
        "/mock/auth/login",
        json={"email": "demo@pegadocs.local", "password": "demo1234"},
    )
    assert response.status_code == 404


def test_mock_login_and_refresh(client):
    login = client.post(
        "/mock/auth/login",
        json={"email": "demo@pegadocs.local", "password": "demo1234"},
    )
    assert login.status_code == 200
    assert login.json()["user_id"] == "mock-user-demo"

    refreshed = client.post(
        "/mock/auth/refresh",
        json={"refresh_token": login.json()["refresh_token"]},
    )
    assert refreshed.status_code == 200
    assert refreshed.json()["access_token"].startswith("mock-access-")


def test_mock_chat_flow(client, auth_headers):
    created = client.post(
        "/mock/add-chat",
        headers=auth_headers,
        json={
            "database_id": "mock-db",
            "collection_id": "mock-collection",
            "chat_name": "Demo chat",
            "chat_source": "web",
            "model_id": "mock-model",
            "prompt_id": "mock-prompt",
        },
    )
    assert created.status_code == 200
    chat_id = created.json()["chat_id"]

    reply = client.post(
        "/mock/chat",
        headers=auth_headers,
        json={"chat_id": chat_id, "message": "Hello"},
    )
    assert reply.status_code == 202
    assert reply.json() == {"response": "Mock response to: Hello"}

    history = client.post(
        "/mock/get-chat-history",
        headers=auth_headers,
        json={"chat_id": chat_id},
    )
    assert history.json() == [
        {"role": "user", "message": "Hello"},
        {"role": "assistant", "message": "Mock response to: Hello"},
    ]

    chats = client.get("/mock/list-chats", headers=auth_headers)
    assert chats.status_code == 200
    assert chats.json()[0]["id"] == chat_id

    deleted = client.delete(f"/mock/delete-chat/{chat_id}", headers=auth_headers)
    assert deleted.status_code == 200


def test_mock_chat_requires_token(client):
    response = client.get("/mock/list-chats")
    assert response.status_code == 401
