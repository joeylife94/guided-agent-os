"""
Tests for Local LLM Client

Tests the LocalLLMClient class and its interactions with an OpenAI-compatible API.
All HTTP calls are mocked.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from app.services.local_llm import LocalLLMClient


class TestLocalLLMClientInit:
    """Test LocalLLMClient initialization."""
    
    def test_init_with_defaults(self):
        """Should initialize with default values."""
        client = LocalLLMClient()
        assert client.base_url == "http://localhost:11434/v1"
        assert client.model == "qwen2.5:7b-instruct"
        assert client.timeout == 30
    
    def test_init_with_custom_values(self):
        """Should accept custom configuration."""
        client = LocalLLMClient(
            base_url="http://custom:8000",
            model="custom-model",
            timeout=60,
        )
        assert client.base_url == "http://custom:8000"
        assert client.model == "custom-model"
        assert client.timeout == 60
    
    def test_init_with_env_vars(self, monkeypatch):
        """Should read from environment variables."""
        monkeypatch.setenv("LOCAL_LLM_BASE_URL", "http://env-url:9000")
        monkeypatch.setenv("LOCAL_LLM_MODEL", "env-model")
        monkeypatch.setenv("LOCAL_LLM_TIMEOUT", "45")
        
        client = LocalLLMClient()
        assert client.base_url == "http://env-url:9000"
        assert client.model == "env-model"
        assert client.timeout == 45

    def test_init_invalid_timeout_env_uses_default(self, monkeypatch):
        """Invalid timeout env values should not crash initialization."""
        monkeypatch.setenv("LOCAL_LLM_TIMEOUT", "not-a-number")

        client = LocalLLMClient()

        assert client.timeout == 30

    def test_init_strips_trailing_base_url_slash(self):
        """Trailing slashes should not produce double-slash API URLs."""
        client = LocalLLMClient(base_url="http://localhost:11434/v1/")

        assert client.base_url == "http://localhost:11434/v1"

    def test_blank_env_vars_use_defaults(self, monkeypatch):
        """Blank env vars should not override safe defaults."""
        monkeypatch.setenv("LOCAL_LLM_BASE_URL", "")
        monkeypatch.setenv("LOCAL_LLM_MODEL", "")

        client = LocalLLMClient()

        assert client.base_url == "http://localhost:11434/v1"
        assert client.model == "qwen2.5:7b-instruct"
    
    def test_init_args_override_env_vars(self, monkeypatch):
        """Constructor args should override environment variables."""
        monkeypatch.setenv("LOCAL_LLM_BASE_URL", "http://env-url:9000")
        monkeypatch.setenv("LOCAL_LLM_MODEL", "env-model")
        
        client = LocalLLMClient(
            base_url="http://args-url:8000",
            model="args-model",
        )
        assert client.base_url == "http://args-url:8000"
        assert client.model == "args-model"


class TestLocalLLMClientChat:
    """Test chat method."""
    
    @patch("app.services.local_llm.requests.post")
    def test_chat_successful_response(self, mock_post):
        """Should successfully parse OpenAI-compatible response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "Hello, this is a response."
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        
        client = LocalLLMClient()
        result = client.chat(
            messages=[
                {"role": "system", "content": "You are helpful."},
                {"role": "user", "content": "Hello"},
            ]
        )
        
        assert result["ok"] is True
        assert result["model"] == "qwen2.5:7b-instruct"
        assert result["content"] == "Hello, this is a response."
        assert "raw" in result
        
        # Verify correct URL was called
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "http://localhost:11434/v1/chat/completions" in call_args[0][0]
    
    @patch("app.services.local_llm.requests.post")
    def test_chat_with_temperature(self, mock_post):
        """Should pass temperature parameter."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Response"}}]
        }
        mock_post.return_value = mock_response
        
        client = LocalLLMClient()
        client.chat(
            messages=[{"role": "user", "content": "Test"}],
            temperature=0.7,
        )
        
        call_kwargs = mock_post.call_args[1]
        assert call_kwargs["json"]["temperature"] == 0.7

    def test_chat_accepts_injected_http_post(self):
        """HTTP transport should be injectable for tests."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Injected response"}}]
        }
        http_post = Mock(return_value=mock_response)

        client = LocalLLMClient(http_post=http_post)
        result = client.chat(messages=[{"role": "user", "content": "Test"}])

        assert result["ok"] is True
        assert result["content"] == "Injected response"
        http_post.assert_called_once()
    
    @patch("app.services.local_llm.requests.post")
    def test_chat_http_error(self, mock_post):
        """Should handle HTTP errors gracefully."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal server error"
        mock_post.return_value = mock_response
        
        client = LocalLLMClient()
        result = client.chat(messages=[{"role": "user", "content": "Test"}])
        
        assert result["ok"] is False
        assert result["model"] == "qwen2.5:7b-instruct"
        assert result["content"] == ""
        assert "HTTP 500" in result["error"]
    
    @patch("app.services.local_llm.requests.post")
    def test_chat_connection_error(self, mock_post):
        """Should handle connection errors gracefully."""
        import requests
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection refused")
        
        client = LocalLLMClient()
        result = client.chat(messages=[{"role": "user", "content": "Test"}])
        
        assert result["ok"] is False
        assert result["content"] == ""
        assert "Connection error" in result["error"]
    
    @patch("app.services.local_llm.requests.post")
    def test_chat_timeout(self, mock_post):
        """Should handle timeout gracefully."""
        import requests
        mock_post.side_effect = requests.exceptions.Timeout()
        
        client = LocalLLMClient(timeout=5)
        result = client.chat(messages=[{"role": "user", "content": "Test"}])
        
        assert result["ok"] is False
        assert result["content"] == ""
        assert "timeout" in result["error"].lower()
    
    def test_chat_no_messages(self):
        """Should handle empty message list."""
        client = LocalLLMClient()
        result = client.chat(messages=[])
        
        assert result["ok"] is False
        assert result["error"] == "No messages provided"
    
    @patch("app.services.local_llm.requests.post")
    def test_chat_unexpected_response_format(self, mock_post):
        """Should handle unexpected response formats."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"unexpected": "format"}
        mock_post.return_value = mock_response
        
        client = LocalLLMClient()
        result = client.chat(messages=[{"role": "user", "content": "Test"}])
        
        assert result["ok"] is False
        assert "Unexpected response format" in result["error"]
    
    @patch("app.services.local_llm.requests.post")
    def test_chat_generic_exception(self, mock_post):
        """Should handle generic exceptions."""
        mock_post.side_effect = Exception("Unexpected error")
        
        client = LocalLLMClient()
        result = client.chat(messages=[{"role": "user", "content": "Test"}])
        
        assert result["ok"] is False
        assert "Unexpected error" in result["error"]
    
    @patch("app.services.local_llm.requests.post")
    def test_chat_returns_normalized_response(self, mock_post):
        """Should return normalized response structure."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "Test response",
                        "role": "assistant",
                    }
                }
            ],
            "model": "some-model",
        }
        mock_post.return_value = mock_response
        
        client = LocalLLMClient()
        result = client.chat(messages=[{"role": "user", "content": "Test"}])
        
        # Check response structure
        assert "ok" in result
        assert "model" in result
        assert "content" in result
        assert "raw" in result
        assert isinstance(result["raw"], dict)
