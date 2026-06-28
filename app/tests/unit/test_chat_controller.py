from unittest.mock import Mock, patch
from uuid import uuid4
from app.application.services.model_service import ModelService
from app.application.services.prompt_service import PromptService
from app.presentation.controllers.chat_controller import ChatController
from app.application.services.chat_service import ChatService
from app.presentation.schemas.chat_schemas import (
    ChatRequest,
    AddChatMetadataRequest,
    GetChatHistoryRequest,
)


class TestChatController:
    """Unit tests for ChatController"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_chat_service = Mock(spec=ChatService)
        self.mock_model_service = Mock(spec=ModelService)
        self.mock_prompt_service = Mock(spec=PromptService)
        self.chat_controller = ChatController(
            self.mock_chat_service, self.mock_model_service, self.mock_prompt_service
        )

    @patch.object(ChatController, "chat_kwargs")
    @patch(
        "app.presentation.controllers.chat_controller.get_embedding_model_id_by_collection_id"
    )
    @patch("app.presentation.controllers.chat_controller.ModelFactory")
    def test_chat_success(
        self, mock_model_factory, mock_get_embedding_model_id, mock_chat_kwargs
    ):
        """Test successful chat operation"""
        request = ChatRequest(
            chat_id="test-chat",
            message="Hello, how are you?",
        )

        mock_get_embedding_model_id.return_value = "embed-model-id"

        self.mock_prompt_service.get_prompt.return_value = {
            "prompt": "You are a helpful assistant."
        }

        mock_llm_model = Mock()
        mock_embedding_model = Mock()
        mock_model_factory_instance = Mock()
        mock_model_factory_instance.get_llm_model.return_value = mock_llm_model
        mock_model_factory_instance.get_embedding_model.return_value = (
            mock_embedding_model
        )
        mock_model_factory.return_value = mock_model_factory_instance
        mock_chat_kwargs.return_value = {
            "collection_id": "test-collection",
            "chat_id": "test-chat",
            "message": "Hello, how are you?",
            "system_prompt": "You are a helpful assistant.",
            "llm_model": mock_llm_model,
            "embedding_model": mock_embedding_model,
        }

        self.mock_chat_service.chat.return_value = "I'm doing well, thank you!"

        result = self.chat_controller.chat(request, "test-user")

        assert result == {"response": "I'm doing well, thank you!"}
        self.mock_chat_service.chat.assert_called_once_with(
            collection_id="test-collection",
            chat_id="test-chat",
            message="Hello, how are you?",
            llm_model=mock_llm_model,
            embedding_model=mock_embedding_model,
            system_prompt="You are a helpful assistant.",
        )

    @patch.object(ChatController, "chat_kwargs")
    @patch(
        "app.presentation.controllers.chat_controller.get_embedding_model_id_by_collection_id"
    )
    @patch("app.presentation.controllers.chat_controller.ModelFactory")
    def test_stream_chat_success(
        self, mock_model_factory, mock_get_embedding_model_id, mock_chat_kwargs
    ):
        """Test successful streaming chat operation"""
        chat_id = str(uuid4())
        request = ChatRequest(
            chat_id=chat_id,
            message="Hello, how are you?",
        )

        mock_get_embedding_model_id.return_value = "embed-model-id"

        mock_llm_model = Mock()
        mock_embedding_model = Mock()
        mock_model_factory_instance = Mock()
        mock_model_factory_instance.get_llm_model.return_value = mock_llm_model
        mock_model_factory_instance.get_embedding_model.return_value = (
            mock_embedding_model
        )
        mock_model_factory.return_value = mock_model_factory_instance

        expected_stream = ["Hello", " ", "there", "!"]
        self.mock_chat_service.stream_chat.return_value = expected_stream
        self.mock_prompt_service.get_prompt.return_value = {
            "prompt": "You are a helpful assistant."
        }

        mock_chat_kwargs.return_value = {
            "collection_id": "test-collection",
            "chat_id": chat_id,
            "message": "Hello, how are you?",
            "system_prompt": "You are a helpful assistant.",
            "llm_model": mock_llm_model,
            "embedding_model": mock_embedding_model,
        }
        result = self.chat_controller.stream_chat(request, "test-user")

        assert result == expected_stream
        self.mock_chat_service.stream_chat.assert_called_once_with(
            collection_id="test-collection",
            chat_id=chat_id,
            message="Hello, how are you?",
            system_prompt="You are a helpful assistant.",
            llm_model=mock_llm_model,
            embedding_model=mock_embedding_model,
        )

    def test_add_chat_success(self):
        """Test successful chat addition"""
        request = AddChatMetadataRequest(
            collection_id="test-collection",
            chat_name="Test Chat",
            database_id="test-database",
            model_id="test-model",
            chat_source="web",
            prompt_id="default-prompt",
        )
        user_id = "test-user"

        self.mock_chat_service.add_chat.return_value = "new-chat-id"

        result = self.chat_controller.add_chat(request, user_id)

        assert result.chat_id == "new-chat-id"
        self.mock_chat_service.add_chat.assert_called_once_with(
            collection_id="test-collection",
            user_id="test-user",
            chat_name="Test Chat",
            database_id="test-database",
            model_id="test-model",
            chat_source="web",
            prompt_id="default-prompt",
        )

    def test_delete_chat_success(self):
        """Test successful chat deletion"""
        chat_id = "test-chat"
        user_id = "test-user"

        result = self.chat_controller.delete_chat(chat_id, user_id)

        assert result.message == "Chat with ID test-chat deleted successfully"
        self.mock_chat_service.delete_chat.assert_called_once_with(user_id, chat_id)

    def test_get_chats_success(self):
        """Test successful chat retrieval"""
        user_id = "test-user"
        mock_chats = [
            {
                "id": "chat1",
                "collection_id": "col1",
                "name": "Chat 1",
                "created_at": "2024-01-01T00:00:00Z",
                "model_id": "model-1",
                "chat_source": "web",
                "prompt_id": "default-prompt",
            },
            {
                "id": "chat2",
                "collection_id": "col2",
                "name": "Chat 2",
                "created_at": "2024-01-02T00:00:00Z",
                "model_id": "model-2",
                "chat_source": "web",
                "prompt_id": "default-prompt",
            },
        ]

        self.mock_chat_service.get_chats.return_value = mock_chats

        result = self.chat_controller.get_chats(user_id)

        assert len(result) == 2
        assert result[0].id == "chat1"
        assert result[0].collection_id == "col1"
        assert result[0].name == "Chat 1"
        assert result[0].created_at == "2024-01-01T00:00:00Z"
        assert result[0].model_id == "model-1"
        assert result[1].id == "chat2"
        assert result[1].collection_id == "col2"
        assert result[1].name == "Chat 2"
        assert result[1].created_at == "2024-01-02T00:00:00Z"
        assert result[1].model_id == "model-2"

        self.mock_chat_service.get_chats.assert_called_once_with("test-user")

    def test_get_chat_history_success(self):
        """Test successful chat history retrieval"""
        request = GetChatHistoryRequest(chat_id="test-chat")

        mock_history = [
            {"role": "user", "message": "Hello"},
            {"role": "assistant", "message": "Hi there!"},
        ]

        self.mock_chat_service.get_chat_metadata.return_value = {
            "collection_id": "test-collection"
        }
        self.mock_chat_service.get_chat_history.return_value = mock_history

        result = self.chat_controller.get_chat_history(request, "test-user")

        assert len(result) == 2
        assert result[0].role == "user"
        assert result[0].message == "Hello"
        assert result[1].role == "assistant"
        assert result[1].message == "Hi there!"

        self.mock_chat_service.get_chat_history.assert_called_once_with(
            collection_id="test-collection", chat_id="test-chat"
        )
