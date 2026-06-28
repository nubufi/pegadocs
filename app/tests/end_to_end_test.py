import requests
from dotenv import load_dotenv
import os

load_dotenv()

base_url = "http://localhost:8000"
base_url = (
    "https://pegadocsbackend.salmonsmoke-9f440359.francecentral.azurecontainerapps.io"
)
test_api_key = os.getenv("TEST_API_KEY")

# Headers with API key
headers = {"X-API-Key": test_api_key} if test_api_key else {}

# Test data
test_collection_name = "test_collection"
test_data_source_name = "test_data_source"
test_website_url = "https://soilprime.com"
test_chat_name = "test_chat"
test_message = "What is this website about?"
test_system_prompt = "You are a helpful assistant."

# Global variables to store IDs between tests
collection_id = None
data_source_id = None
chat_id = None
task_id = None


def create_collection():
    """Test creating a new collection"""
    global collection_id

    url = f"{base_url}/add-collection"
    payload = {"collection_name": test_collection_name}

    response = requests.post(url, json=payload, headers=headers)

    print(response.text)  # Print the response for debugging
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"

    data = response.json()
    assert "collection_id" in data, "Response should contain collection_id"

    collection_id = data["collection_id"]

    return collection_id


def create_data_source():
    """Test creating a new data source"""
    global data_source_id

    if not collection_id:
        raise ValueError("Collection ID not available. Run create_collection first.")

    url = f"{base_url}/add-data-source"
    payload = {
        "collection_id": collection_id,
        "data_source_name": test_data_source_name,
        "data_source_type": "website",
    }

    response = requests.post(url, json=payload, headers=headers)

    assert response.status_code == 201, f"Expected 201, got {response.status_code}"

    data = response.json()
    assert "data_source_id" in data, "Response should contain data_source_id"

    data_source_id = data["data_source_id"]

    return data_source_id


def list_data_sources():
    """Test listing data sources in a collection"""
    if not collection_id:
        raise ValueError("Collection ID not available. Run create_collection first.")

    url = f"{base_url}/list-data-sources"
    payload = {"collection_id": collection_id}

    response = requests.post(url, json=payload, headers=headers)

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    data = response.json()
    assert isinstance(data, list), "Response should be a list"

    # Check if our created data source is in the list
    data_source_found = any(ds["id"] == data_source_id for ds in data)
    assert data_source_found, "Created data source should be in the list"

    return data


def list_collections():
    """Test listing all collections"""
    url = f"{base_url}/list-collections"

    response = requests.get(url, headers=headers)

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    data = response.json()
    assert isinstance(data, list), "Response should be a list"

    # Check if our created collection is in the list
    collection_found = any(col["id"] == collection_id for col in data)
    assert collection_found, "Created collection should be in the list"

    return data


def embed_website():
    """Test embedding a website"""
    global task_id

    if not collection_id or not data_source_id:
        raise ValueError(
            "Collection ID and Data Source ID not available. Run create_collection and create_data_source first."
        )

    url = f"{base_url}/embed-website"
    payload = {
        "data_source_id": data_source_id,
        "collection_id": collection_id,
        "website_url": test_website_url,
        "excluded_paths": ["/admin", "/private"],
    }

    response = requests.post(url, json=payload, headers=headers)

    assert response.status_code == 202, f"Expected 202, got {response.status_code}"

    data = response.json()
    assert "task_id" in data, "Response should contain task_id"

    task_id = data["task_id"]

    return task_id


def check_status():
    """Test checking task status"""
    from time import sleep

    sleep(10)
    if not task_id:
        raise ValueError("Task ID not available. Run embed_website first.")

    url = f"{base_url}/scan/task/{task_id}"

    response = requests.get(url, headers=headers)

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    data = response.json()
    assert "task_id" in data, "Response should contain task_id"
    assert "status" in data, "Response should contain status"
    assert data["task_id"] == task_id, "Task ID should match"

    return data


def chat():
    """Test basic chat functionality"""
    if not collection_id:
        raise ValueError("Collection ID not available. Run create_collection first.")

    # First create a chat
    chat_url = f"{base_url}/add-chat"
    chat_payload = {"collection_id": collection_id, "chat_name": test_chat_name}

    chat_response = requests.post(chat_url, json=chat_payload, headers=headers)

    assert (
        chat_response.status_code == 200
    ), f"Expected 200, got {chat_response.status_code}"

    chat_data = chat_response.json()
    assert "chat_id" in chat_data, "Response should contain chat_id"

    global chat_id
    chat_id = chat_data["chat_id"]

    # Now test the chat endpoint
    url = f"{base_url}/chat"
    payload = {
        "chat_id": chat_id,
        "collection_id": collection_id,
        "message": test_message,
        "system_prompt": test_system_prompt,
    }

    response = requests.post(url, json=payload, headers=headers)

    assert response.status_code == 202, f"Expected 202, got {response.status_code}"

    data = response.json()

    return data


def chat_with_history():
    """Test chat with history functionality"""
    if not collection_id or not chat_id:
        raise ValueError(
            "Collection ID and Chat ID not available. Run create_collection and chat first."
        )

    url = f"{base_url}/get-chat-history"
    payload = {"chat_id": chat_id, "collection_id": collection_id}

    response = requests.post(url, json=payload, headers=headers)

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    data = response.json()
    assert isinstance(data, list), "Response should be a list"

    return data


def list_chat_history():
    """Test listing all chats for a user"""
    url = f"{base_url}/list-chats"

    response = requests.get(url, headers=headers)

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    data = response.json()
    assert isinstance(data, list), "Response should be a list"

    # Check if our created chat is in the list
    chat_found = any(chat["id"] == chat_id for chat in data)
    assert chat_found, "Created chat should be in the list"

    return data


def delete_chat_history():
    """Test deleting a chat"""
    if not collection_id or not chat_id:
        raise ValueError(
            "Collection ID and Chat ID not available. Run create_collection and chat first."
        )

    url = f"{base_url}/delete-chat"
    payload = {"collection_id": collection_id, "chat_id": chat_id}

    response = requests.post(url, json=payload, headers=headers)

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    data = response.json()
    assert "message" in data, "Response should contain message"

    return data


def delete_data_source():
    """Test deleting a data source"""
    if not collection_id or not data_source_id:
        raise ValueError(
            "Collection ID and Data Source ID not available. Run create_collection and create_data_source first."
        )

    url = f"{base_url}/delete-data-source"
    payload = {"collection_id": collection_id, "data_source_id": data_source_id}

    response = requests.post(url, json=payload, headers=headers)

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    data = response.json()
    return data


def delete_collection():
    """Test deleting a collection"""
    if not collection_id:
        raise ValueError("Collection ID not available. Run create_collection first.")

    url = f"{base_url}/delete-collection"
    payload = {"collection_id": collection_id, "delete_data_sources": True}

    response = requests.post(url, json=payload, headers=headers)

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    data = response.json()
    return data


def run_all_tests():
    """Run all tests in the specified order"""
    print("=" * 50)
    print("Starting End-to-End Tests")
    print("=" * 50)

    try:
        # Test 1: Create collection
        print("\n1. Testing create_collection...")
        create_collection()

        # Test 2: Create data source
        print("\n2. Testing create_data_source...")
        create_data_source()

        # Test 3: List data sources
        print("\n3. Testing list_data_sources...")
        list_data_sources()

        # Test 4: List collections
        print("\n4. Testing list_collections...")
        list_collections()

        # Test 5: Embed website
        print("\n5. Testing embed_website...")
        embed_website()

        # Test 6: Check status
        print("\n6. Testing check_status...")
        check_status()

        # Test 7: Chat
        print("\n7. Testing chat...")
        chat()

        # Test 8: Chat with history
        print("\n8. Testing chat_with_history...")
        chat_with_history()

        # Test 9: List chat history
        print("\n9. Testing list_chat_history...")
        list_chat_history()

        # Test 10: Delete chat history
        print("\n10. Testing delete_chat_history...")
        delete_chat_history()

        # Test 11: Delete data source
        print("\n11. Testing delete_data_source...")
        delete_data_source()

        # Test 12: Delete collection
        print("\n12. Testing delete_collection...")
        delete_collection()

        print("\n" + "=" * 50)
        print("All tests completed successfully!")
        print("=" * 50)

    except Exception as e:
        print(f"\nTest failed with error: {str(e)}")
        raise
    finally:
        # Clean up resources if they exist
        try:
            if collection_id:
                delete_collection()
        except:
            pass
        try:
            if data_source_id:
                delete_data_source()
        except:
            pass


if __name__ == "__main__":
    run_all_tests()
