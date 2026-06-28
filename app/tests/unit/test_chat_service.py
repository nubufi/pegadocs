from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.llms.utils import LLMType

from app.application.exceptions import (
    ChatDeleteException,
    ChatFailedException,
    ChatMetadataAddException,
    ChatMetadataFetchException,
    ChatNotFoundException,
    CollectionNotFoundException,
)
from app.application.protocols.chat_store_protocol import ChatStoreProtocol
from app.application.protocols.vector_store_protocol import VectorStoreProtocol
from app.application.services.chat_service import ChatService


class TestChatService:
    def setup_method(self):
        self.mock_vector_store = Mock(spec=VectorStoreProtocol)
        self.mock_chat_store = Mock(spec=ChatStoreProtocol)
        self.mock_chat_store.chat_id = "chatid"
        self.mock_llm_model = Mock(spec=LLMType)
        self.mock_llm_model.input_price_per_1k_tokens = 0.001
        self.mock_llm_model.output_price_per_1k_tokens = 0.002
        self.mock_embedding_model = Mock(spec=BaseEmbedding)
        self.mock_embedding_model.input_price_per_1k_tokens = 0.0001
        self.chat_service = ChatService(self.mock_vector_store, self.mock_chat_store)

    def test_chat_success(self):
        self.mock_vector_store.check_collection.return_value = True
        mock_engine = Mock()
        mock_engine.chat.return_value = SimpleNamespace(response="response")
        self.mock_chat_store.get_chat_engine.return_value = mock_engine

        response = self.chat_service.chat(
            "cid",
            "chatid",
            "hello",
            self.mock_llm_model,
            self.mock_embedding_model,
            "prompt",
            "user_id",
        )
        assert response == "response"
        mock_engine.chat.assert_called_once_with("hello")

    def test_chat_collection_not_found(self):
        self.mock_vector_store.check_collection.return_value = False
        with pytest.raises(CollectionNotFoundException):
            self.chat_service.chat(
                "cid",
                "chatid",
                "hello",
                self.mock_llm_model,
                self.mock_embedding_model,
                "prompt",
                "user_id",
            )

    def test_chat_failure(self):
        self.mock_vector_store.check_collection.return_value = True
        mock_engine = Mock()
        mock_engine.chat.side_effect = Exception("boom")
        self.mock_chat_store.get_chat_engine.return_value = mock_engine

        with pytest.raises(
            ChatFailedException, match="Failed to process chat message: boom"
        ):
            self.chat_service.chat(
                "cid",
                "chatid",
                "hello",
                self.mock_llm_model,
                self.mock_embedding_model,
                "prompt",
                "user_id",
            )

    def test_stream_chat_success(self):
        self.mock_vector_store.check_collection.return_value = True
        mock_engine = Mock()
        mock_engine.stream_chat.return_value = SimpleNamespace(
            response_gen=iter(["A", "B"])
        )
        self.mock_chat_store.get_chat_engine.return_value = mock_engine

        result = list(
            self.chat_service.stream_chat(
                "cid",
                "chatid",
                "hello",
                self.mock_llm_model,
                self.mock_embedding_model,
                "prompt",
                "user_id",
            )
        )
        assert result == ["A", "B"]

    def test_stream_chat_collection_not_found(self):
        self.mock_vector_store.check_collection.return_value = False
        with pytest.raises(CollectionNotFoundException):
            self.chat_service.stream_chat(
                "cid",
                "chatid",
                "hello",
                self.mock_llm_model,
                self.mock_embedding_model,
                "prompt",
                "user_id",
            )

    def test_stream_chat_failure(self):
        self.mock_vector_store.check_collection.return_value = True
        mock_engine = Mock()
        mock_engine.stream_chat.side_effect = Exception("stream-error")
        self.mock_chat_store.get_chat_engine.return_value = mock_engine

        with pytest.raises(
            ChatFailedException,
            match="Failed to stream chat messages: stream-error",
        ):
            list(
                self.chat_service.stream_chat(
                    "cid",
                    "chatid",
                    "hello",
                    self.mock_llm_model,
                    self.mock_embedding_model,
                    "prompt",
                    "user_id",
                )
            )

    def test_add_chat_success(self):
        with patch("app.application.services.chat_service.add_item") as mock_add:
            mock_add.return_value = Mock(data=[{"id": "chatid"}])
            result = self.chat_service.add_chat(
                "cid", "uid", "test", "dbid", "model_id", "web", "default"
            )
            assert result == "chatid"

    def test_add_chat_failure(self):
        with patch("app.application.services.chat_service.add_item") as mock_add:
            mock_add.side_effect = Exception("fail")
            with pytest.raises(
                ChatMetadataAddException, match="Failed to add chat metadata: fail"
            ):
                self.chat_service.add_chat(
                    "cid", "uid", "test", "dbid", "model_id", "web", "default"
                )

    def test_get_chats_success(self):
        with patch("app.application.services.chat_service.fetch_items") as mock_fetch:
            mock_fetch.return_value = [{"id": "chat1"}]
            result = self.chat_service.get_chats("uid")
            assert result == [{"id": "chat1"}]

    def test_get_chats_failure(self):
        with patch("app.application.services.chat_service.fetch_items") as mock_fetch:
            mock_fetch.side_effect = Exception("error")
            with pytest.raises(
                ChatMetadataFetchException, match="Failed to fetch chat metadata: error"
            ):
                self.chat_service.get_chats("uid")

    def test_get_chat_history_success(self):
        self.mock_vector_store.check_collection.return_value = True
        self.mock_chat_store.get_chat_history.return_value = [{"msg": "hello"}]
        result = self.chat_service.get_chat_history("cid", "chatid")
        assert result == [{"msg": "hello"}]

    def test_get_chat_history_collection_not_found(self):
        self.mock_vector_store.check_collection.return_value = False
        with pytest.raises(CollectionNotFoundException):
            self.chat_service.get_chat_history("cid", "chatid")

    def test_get_chat_history_failure(self):
        self.mock_vector_store.check_collection.return_value = True
        self.mock_chat_store.get_chat_history.side_effect = Exception("boom")
        with pytest.raises(ChatNotFoundException, match="Chat chatid not found: boom"):
            self.chat_service.get_chat_history("cid", "chatid")

    def test_delete_chat_success(self):
        with patch("app.application.services.chat_service.delete_item") as mock_delete:
            mock_delete.return_value = None
            self.chat_service.delete_chat("test-user", "test-chat")
            self.mock_chat_store.delete_chat.assert_called_once()

    def test_delete_chat_failure(self):
        self.mock_chat_store.delete_chat.side_effect = Exception("err")
        with pytest.raises(ChatDeleteException, match="Failed to delete chat: err"):
            self.chat_service.delete_chat("test-user", "test-chat")
