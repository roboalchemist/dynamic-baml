"""
Tests for the dynamic_baml.providers module.
"""

import json
import pytest
from unittest import TestCase
from unittest.mock import patch, MagicMock, Mock
import httpx
import os

from dynamic_baml.providers import (
    LLMProvider, OllamaProvider, OpenRouterProvider, LLMProviderFactory
)
from dynamic_baml.exceptions import LLMProviderError


class TestOllamaProvider(TestCase):
    """Test cases for OllamaProvider class."""

    def setUp(self):
        """Set up test fixtures."""
        self.provider = OllamaProvider()

    def test_initialization_default_url(self):
        """Test OllamaProvider initialization with default URL."""
        provider = OllamaProvider()
        assert provider.base_url == "http://localhost:11434"

    def test_initialization_custom_url(self):
        """Test OllamaProvider initialization with custom URL."""
        custom_url = "http://custom-ollama:8080"
        provider = OllamaProvider(custom_url)
        assert provider.base_url == custom_url

    def test_initialization_strips_trailing_slash(self):
        """Test that trailing slash is stripped from base URL."""
        provider = OllamaProvider("http://localhost:11434/")
        assert provider.base_url == "http://localhost:11434"

    @patch('httpx.Client')
    def test_call_success(self, mock_client_class):
        """Test successful LLM call through Ollama."""
        mock_response = Mock()
        mock_response.json.return_value = {"response": "Hello, world!"}
        mock_response.raise_for_status.return_value = None
        
        # Create a mock that properly handles context manager
        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client_class.return_value = mock_client

        result = self.provider.call("Test prompt", {"model": "gemma3:1b"})
        
        assert result == "Hello, world!"
        mock_client.post.assert_called_once()

    @patch('httpx.Client')
    def test_call_with_custom_options(self, mock_client_class):
        """Test call with custom temperature and model."""
        mock_response = Mock()
        mock_response.json.return_value = {"response": "Custom response"}
        mock_response.raise_for_status.return_value = None
        
        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client_class.return_value = mock_client

        options = {
            "model": "codellama:7b",
            "temperature": 0.7,
            "timeout": 60
        }
        
        result = self.provider.call("Custom prompt", options)
        
        assert result == "Custom response"
        
        # Verify the request was made with correct parameters
        call_args = mock_client.post.call_args
        json_data = call_args[1]["json"]
        assert json_data["model"] == "codellama:7b"
        assert json_data["options"]["temperature"] == 0.7

    @patch('httpx.Client')
    def test_call_http_status_error(self, mock_client_class):
        """Test handling of HTTP status errors."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Model not found"
        
        mock_client = Mock()
        mock_client.post.side_effect = httpx.HTTPStatusError(
            "404 Not Found", request=Mock(), response=mock_response
        )
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client_class.return_value = mock_client

        with pytest.raises(LLMProviderError) as exc_info:
            self.provider.call("Test prompt", {})

        assert "Ollama API error 404" in str(exc_info.value)
        assert exc_info.value.provider == "ollama"
        assert exc_info.value.context["status_code"] == 404

    @patch('httpx.Client')
    def test_call_request_error(self, mock_client_class):
        """Test handling of request errors (connection issues)."""
        mock_client = Mock()
        mock_client.post.side_effect = httpx.RequestError("Connection refused")
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client_class.return_value = mock_client

        with pytest.raises(LLMProviderError) as exc_info:
            self.provider.call("Test prompt", {})

        assert "Ollama connection error" in str(exc_info.value)
        assert exc_info.value.provider == "ollama"

    @patch('httpx.Client')
    def test_call_unexpected_error(self, mock_client_class):
        """Test handling of unexpected errors."""
        mock_client = Mock()
        mock_client.post.side_effect = ValueError("Unexpected error")
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client_class.return_value = mock_client

        with pytest.raises(LLMProviderError) as exc_info:
            self.provider.call("Test prompt", {})

        assert "Unexpected Ollama error" in str(exc_info.value)
        assert exc_info.value.provider == "ollama"

    @patch('httpx.Client')
    def test_is_available_true(self, mock_client_class):
        """Test is_available returns True when Ollama is accessible."""
        mock_response = Mock()
        mock_response.status_code = 200
        
        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client_class.return_value = mock_client

        assert self.provider.is_available() is True

    @patch('httpx.Client')
    def test_is_available_false(self, mock_client_class):
        """Test is_available returns False when Ollama is not accessible."""
        mock_client = Mock()
        mock_client.get.side_effect = httpx.RequestError("Connection refused")
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client_class.return_value = mock_client

        assert self.provider.is_available() is False

    def test_custom_base_url(self):
        """Test provider with custom base URL."""
        custom_provider = OllamaProvider("http://custom-ollama:11434")
        assert custom_provider.base_url == "http://custom-ollama:11434"

    def test_base_url_strip_trailing_slash(self):
        """Test that trailing slash is stripped from base URL."""
        custom_provider = OllamaProvider("http://localhost:11434/")
        assert custom_provider.base_url == "http://localhost:11434"


class TestOpenRouterProvider(TestCase):
    """Test cases for OpenRouterProvider class."""

    def setUp(self):
        """Set up test fixtures."""
        self.api_key = "test_api_key_12345"
        self.provider = OpenRouterProvider(self.api_key)

    def test_initialization_with_api_key(self):
        """Test OpenRouterProvider initialization with API key."""
        provider = OpenRouterProvider("my-api-key")
        assert provider.api_key == "my-api-key"
        assert provider.base_url == "https://openrouter.ai/api/v1"

    @patch.dict('os.environ', {'OPENROUTER_API_KEY': 'env-api-key'})
    def test_initialization_from_environment(self):
        """Test OpenRouterProvider initialization from environment variable."""
        provider = OpenRouterProvider()
        assert provider.api_key == "env-api-key"

    def test_initialization_no_api_key(self):
        """Test OpenRouterProvider initialization without API key."""
        with patch.dict('os.environ', {}, clear=True):
            provider = OpenRouterProvider()
            assert provider.api_key is None

    @patch('httpx.Client')
    def test_call_success(self, mock_client_class):
        """Test successful LLM call through OpenRouter."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [
                {"message": {"content": "Hello from OpenRouter!"}}
            ]
        }
        mock_response.raise_for_status.return_value = None
        
        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client_class.return_value = mock_client

        result = self.provider.call("Test prompt", {"model": "gpt-4"})
        
        assert result == "Hello from OpenRouter!"
        mock_client.post.assert_called_once()

    def test_call_no_api_key(self):
        """Test error when no API key is provided."""
        provider = OpenRouterProvider()
        
        with pytest.raises(LLMProviderError) as exc_info:
            provider.call("Test prompt", {})

        assert "OpenRouter API key not found" in str(exc_info.value)
        assert exc_info.value.provider == "openrouter"

    @patch('httpx.Client')
    def test_call_with_custom_options(self, mock_client_class):
        """Test call with custom temperature and max_tokens."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Custom response"}}]
        }
        mock_response.raise_for_status.return_value = None
        
        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client_class.return_value = mock_client

        options = {
            "model": "claude-3-opus",
            "temperature": 0.8,
            "max_tokens": 2048,
            "timeout": 90
        }
        
        result = self.provider.call("Custom prompt", options)
        
        assert result == "Custom response"
        
        # Verify the request was made with correct parameters
        call_args = mock_client.post.call_args
        json_data = call_args[1]["json"]
        assert json_data["model"] == "claude-3-opus"
        assert json_data["temperature"] == 0.8
        assert json_data["max_tokens"] == 2048

    @patch('httpx.Client')
    def test_call_http_status_error(self, mock_client_class):
        """Test error handling for HTTP status errors."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        
        mock_client = Mock()
        mock_client.post.side_effect = httpx.HTTPStatusError(
            "401 Unauthorized", request=Mock(), response=mock_response
        )
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client_class.return_value = mock_client

        with pytest.raises(LLMProviderError) as exc_info:
            self.provider.call("Test prompt", {})

        assert "OpenRouter API error 401" in str(exc_info.value)
        assert exc_info.value.provider == "openrouter"

    @patch('httpx.Client')
    def test_call_http_status_error_with_json_error(self, mock_client_class):
        """Test handling of HTTP status errors with JSON error details."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": {"message": "Invalid model specified"}
        }
        
        mock_client = Mock()
        mock_client.post.side_effect = httpx.HTTPStatusError(
            "400 Bad Request", request=Mock(), response=mock_response
        )
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client_class.return_value = mock_client

        with pytest.raises(LLMProviderError) as exc_info:
            self.provider.call("Test prompt", {})

        assert "OpenRouter API error 400: Invalid model specified" in str(exc_info.value)

    @patch('httpx.Client')
    def test_call_http_status_error_json_parse_failure(self, mock_client_class):
        """Test handling of HTTP status errors when JSON parsing fails."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        # Make json() method raise an exception to trigger the except clause on line 159
        mock_response.json.side_effect = ValueError("Invalid JSON")
        
        mock_client = Mock()
        mock_client.post.side_effect = httpx.HTTPStatusError(
            "500 Internal Server Error", request=Mock(), response=mock_response
        )
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client_class.return_value = mock_client

        with pytest.raises(LLMProviderError) as exc_info:
            self.provider.call("Test prompt", {})

        assert "OpenRouter API error 500: Internal Server Error" in str(exc_info.value)

    @patch('httpx.Client')
    def test_call_request_error(self, mock_client_class):
        """Test handling of request errors."""
        mock_client = Mock()
        mock_client.post.side_effect = httpx.RequestError("Connection failed")
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client_class.return_value = mock_client

        with pytest.raises(LLMProviderError) as exc_info:
            self.provider.call("Test prompt", {})

        assert "OpenRouter connection error" in str(exc_info.value)
        assert exc_info.value.provider == "openrouter"

    @patch('httpx.Client')
    def test_call_unexpected_error(self, mock_client_class):
        """Test handling of unexpected errors."""
        mock_client = Mock()
        mock_client.post.side_effect = RuntimeError("Unexpected runtime error")
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client_class.return_value = mock_client

        with pytest.raises(LLMProviderError) as exc_info:
            self.provider.call("Test prompt", {})

        assert "Unexpected OpenRouter error" in str(exc_info.value)
        assert exc_info.value.provider == "openrouter"

    @patch('httpx.Client')
    def test_call_no_choices_in_response(self, mock_client_class):
        """Test handling when response has no choices."""
        mock_response = Mock()
        mock_response.json.return_value = {"usage": {"total_tokens": 10}}  # No "choices" key
        mock_response.raise_for_status.return_value = None
        
        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client_class.return_value = mock_client

        with pytest.raises(LLMProviderError) as exc_info:
            self.provider.call("Test prompt", {})

        assert "No response choices returned from OpenRouter" in str(exc_info.value)
        assert exc_info.value.provider == "openrouter"

    @patch('httpx.Client')
    def test_call_empty_choices_in_response(self, mock_client_class):
        """Test handling when response has empty choices."""
        mock_response = Mock()
        mock_response.json.return_value = {"choices": []}  # Empty choices list
        mock_response.raise_for_status.return_value = None
        
        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client_class.return_value = mock_client

        with pytest.raises(LLMProviderError) as exc_info:
            self.provider.call("Test prompt", {})

        assert "No response choices returned from OpenRouter" in str(exc_info.value)

    def test_is_available_with_api_key(self):
        """Test is_available returns True when API key is configured."""
        assert self.provider.is_available() is True

    def test_is_available_without_api_key(self):
        """Test is_available returns False when API key is not configured."""
        provider = OpenRouterProvider(None)
        assert provider.is_available() is False

    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "env_api_key"})
    def test_api_key_from_environment(self):
        """Test that API key is loaded from environment variable."""
        provider = OpenRouterProvider()
        assert provider.api_key == "env_api_key"


class TestLLMProviderFactory(TestCase):
    """Test cases for LLMProviderFactory class."""

    def setUp(self):
        """Set up test fixtures."""
        self.factory = LLMProviderFactory()

    def test_create_ollama_provider(self):
        """Test creating Ollama provider."""
        options = {"provider": "ollama"}
        provider = self.factory.create_provider(options)
        
        assert isinstance(provider, OllamaProvider)
        assert provider.base_url == "http://localhost:11434"

    def test_create_ollama_provider_with_custom_url(self):
        """Test creating Ollama provider with custom base URL."""
        options = {
            "provider": "ollama",
            "base_url": "http://custom-host:8080"
        }
        provider = self.factory.create_provider(options)
        
        assert isinstance(provider, OllamaProvider)
        assert provider.base_url == "http://custom-host:8080"

    def test_create_openrouter_provider(self):
        """Test creating OpenRouter provider."""
        options = {"provider": "openrouter"}
        provider = self.factory.create_provider(options)
        
        assert isinstance(provider, OpenRouterProvider)

    def test_create_openrouter_provider_with_api_key(self):
        """Test creating OpenRouter provider with custom API key."""
        options = {
            "provider": "openrouter",
            "api_key": "custom_key_123"
        }
        provider = self.factory.create_provider(options)
        
        assert isinstance(provider, OpenRouterProvider)
        assert provider.api_key == "custom_key_123"

    def test_create_provider_default_ollama(self):
        """Test that Ollama is the default provider."""
        options = {}  # No provider specified
        provider = self.factory.create_provider(options)
        
        assert isinstance(provider, OllamaProvider)

    def test_create_provider_case_insensitive(self):
        """Test that provider type is case insensitive."""
        options = {"provider": "OPENROUTER"}
        provider = self.factory.create_provider(options)
        
        assert isinstance(provider, OpenRouterProvider)

    def test_create_provider_unknown_type(self):
        """Test error when unknown provider type is specified."""
        options = {"provider": "unknown_provider"}
        
        with pytest.raises(LLMProviderError) as exc_info:
            self.factory.create_provider(options)

        assert "Unknown provider type: unknown_provider" in str(exc_info.value)
        assert exc_info.value.provider == "factory"

    @patch.object(OllamaProvider, 'is_available')
    @patch.object(OpenRouterProvider, 'is_available')
    def test_get_available_providers_both_available(self, mock_openrouter_available, mock_ollama_available):
        """Test getting available providers when both are available."""
        mock_ollama_available.return_value = True
        mock_openrouter_available.return_value = True
        
        available = self.factory.get_available_providers()
        
        assert "ollama" in available
        assert "openrouter" in available
        assert len(available) == 2

    @patch.object(OllamaProvider, 'is_available')
    @patch.object(OpenRouterProvider, 'is_available')
    def test_get_available_providers_only_ollama(self, mock_openrouter_available, mock_ollama_available):
        """Test getting available providers when only Ollama is available."""
        mock_ollama_available.return_value = True
        mock_openrouter_available.return_value = False
        
        available = self.factory.get_available_providers()
        
        assert "ollama" in available
        assert "openrouter" not in available
        assert len(available) == 1

    @patch.object(OllamaProvider, 'is_available')
    @patch.object(OpenRouterProvider, 'is_available')
    def test_get_available_providers_none_available(self, mock_openrouter_available, mock_ollama_available):
        """Test getting available providers when none are available."""
        mock_ollama_available.return_value = False
        mock_openrouter_available.return_value = False
        
        available = self.factory.get_available_providers()
        
        assert len(available) == 0

    @patch.object(OllamaProvider, '__init__')
    @patch.object(OllamaProvider, 'is_available')
    @patch.object(OpenRouterProvider, 'is_available')
    def test_get_available_providers_with_ollama_exception(self, mock_openrouter_available, mock_ollama_available, mock_ollama_init):
        """Test getting available providers when Ollama creation raises exception."""
        # Make OllamaProvider.__init__ raise an exception
        mock_ollama_init.side_effect = Exception("Ollama initialization failed")
        mock_openrouter_available.return_value = True
        
        available = self.factory.get_available_providers()
        
        # Should only have openrouter, ollama should be skipped due to exception
        assert "ollama" not in available
        assert "openrouter" in available
        assert len(available) == 1

    @patch.object(OllamaProvider, 'is_available')
    @patch.object(OpenRouterProvider, '__init__')
    @patch.object(OpenRouterProvider, 'is_available')
    def test_get_available_providers_with_openrouter_exception(self, mock_openrouter_available, mock_openrouter_init, mock_ollama_available):
        """Test getting available providers when OpenRouter creation raises exception."""
        mock_ollama_available.return_value = True
        # Make OpenRouterProvider.__init__ raise an exception
        mock_openrouter_init.side_effect = Exception("OpenRouter initialization failed")
        
        available = self.factory.get_available_providers()
        
        # Should only have ollama, openrouter should be skipped due to exception
        assert "ollama" in available
        assert "openrouter" not in available
        assert len(available) == 1


class TestAbstractLLMProvider(TestCase):
    """Test cases for the abstract LLMProvider base class."""

    def test_cannot_instantiate_abstract_class(self):
        """Test that the abstract LLMProvider class cannot be instantiated directly."""
        with pytest.raises(TypeError):
            LLMProvider()

    def test_abstract_methods_must_be_implemented(self):
        """Test that subclasses must implement abstract methods."""
        class IncompleteProvider(LLMProvider):
            # Missing implementation of call() and is_available()
            pass
        
        with pytest.raises(TypeError):
            IncompleteProvider()

    def test_abstract_methods_signature(self):
        """Test that abstract methods have correct signatures."""
        # This tests that the abstract methods are properly defined
        # The actual implementations are tested in the concrete provider tests
        
        class CompleteProvider(LLMProvider):
            def call(self, prompt: str, options) -> str:
                return "test response"
            
            def is_available(self) -> bool:
                return True
        
        # Should be able to instantiate a complete implementation
        provider = CompleteProvider()
        assert provider.call("test", {}) == "test response"
        assert provider.is_available() is True 