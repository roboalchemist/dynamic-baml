"""
LLM Provider abstractions for different AI services.
"""

import json
import os
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List

import httpx
from .exceptions import LLMProviderError
from .types import ProviderOptions


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def call(self, prompt: str, options: ProviderOptions) -> str:
        """
        Call the LLM with a prompt and return the response.
        
        Args:
            prompt: The prompt text
            options: Provider-specific options
            
        Returns:
            Raw response text from the LLM
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available and properly configured."""
        pass


class OllamaProvider(LLMProvider):
    """Provider for local Ollama models."""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url.rstrip("/")
        
    def call(self, prompt: str, options: ProviderOptions) -> str:
        """Execute LLM call through Ollama API."""
        model = options.get("model", "gemma3:1b")
        timeout = options.get("timeout", 120)
        
        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": options.get("temperature", 0.1),
                        }
                    }
                )
                response.raise_for_status()
                
                result = response.json()
                return result.get("response", "")
                
        except httpx.HTTPStatusError as e:
            raise LLMProviderError(
                f"Ollama API error {e.response.status_code}: {e.response.text}",
                "ollama",
                {"status_code": e.response.status_code}
            ) from e
        except httpx.RequestError as e:
            raise LLMProviderError(
                f"Ollama connection error: {str(e)}",
                "ollama"
            ) from e
        except Exception as e:
            raise LLMProviderError(
                f"Unexpected Ollama error: {str(e)}",
                "ollama"
            ) from e
    
    def is_available(self) -> bool:
        """Check if Ollama is running and accessible."""
        try:
            with httpx.Client(timeout=5) as client:
                response = client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except:
            return False


class OpenRouterProvider(LLMProvider):
    """Provider for OpenRouter cloud models."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"
        
    def call(self, prompt: str, options: ProviderOptions) -> str:
        """Execute LLM call through OpenRouter API."""
        model = options.get("model", "google/gemini-2.0-flash-exp")
        timeout = options.get("timeout", 120)
        
        if not self.api_key:
            raise LLMProviderError(
                "OpenRouter API key not found. Set OPENROUTER_API_KEY environment variable.",
                "openrouter"
            )
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/yourusername/dynamic-baml",
                "X-Title": "Dynamic BAML Library"
            }
            
            with httpx.Client(timeout=timeout) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json={
                        "model": model,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": options.get("temperature", 0.1),
                        "max_tokens": options.get("max_tokens", 4096)
                    }
                )
                response.raise_for_status()
                
                result = response.json()
                if "choices" not in result or not result["choices"]:
                    raise LLMProviderError(
                        "No response choices returned from OpenRouter",
                        "openrouter"
                    )
                
                return result["choices"][0]["message"]["content"]
                
        except httpx.HTTPStatusError as e:
            error_detail = ""
            try:
                error_data = e.response.json()
                error_detail = error_data.get("error", {}).get("message", "")
            except:
                error_detail = e.response.text
            
            raise LLMProviderError(
                f"OpenRouter API error {e.response.status_code}: {error_detail}",
                "openrouter",
                {"status_code": e.response.status_code}
            ) from e
        except httpx.RequestError as e:
            raise LLMProviderError(
                f"OpenRouter connection error: {str(e)}",
                "openrouter"
            ) from e
        except Exception as e:
            raise LLMProviderError(
                f"Unexpected OpenRouter error: {str(e)}",
                "openrouter"
            ) from e
    
    def is_available(self) -> bool:
        """Check if OpenRouter API key is configured."""
        return self.api_key is not None


class LLMProviderFactory:
    """Factory for creating LLM provider instances."""
    
    def create_provider(self, options: ProviderOptions) -> LLMProvider:
        """
        Create an appropriate LLM provider based on options.
        
        Args:
            options: Configuration options including provider type
            
        Returns:
            Configured LLM provider instance
        """
        provider_type = options.get("provider", "ollama").lower()
        
        if provider_type == "ollama":
            base_url = options.get("base_url", "http://localhost:11434")
            return OllamaProvider(base_url)
        elif provider_type == "openrouter":
            api_key = options.get("api_key")
            return OpenRouterProvider(api_key)
        else:
            raise LLMProviderError(
                f"Unknown provider type: {provider_type}",
                "factory"
            )
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider types."""
        providers = []
        
        # Check Ollama
        try:
            ollama = OllamaProvider()
            if ollama.is_available():
                providers.append("ollama")
        except:
            pass
        
        # Check OpenRouter
        try:
            openrouter = OpenRouterProvider()
            if openrouter.is_available():
                providers.append("openrouter")
        except:
            pass
        
        return providers 