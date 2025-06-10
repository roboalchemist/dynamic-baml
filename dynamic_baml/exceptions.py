"""
Exception classes for the Dynamic BAML library.
"""

from typing import Dict, Any, Optional


class DynamicBAMLError(Exception):
    """Base exception class for all Dynamic BAML library errors."""
    
    def __init__(self, message: str, error_type: str = "unknown", context: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.context = context or {}


class SchemaGenerationError(DynamicBAMLError):
    """Raised when schema generation from dictionary fails."""
    
    def __init__(self, message: str, schema_dict: dict = None, context: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "schema_generation", context)
        self.schema_dict = schema_dict


class BAMLCompilationError(DynamicBAMLError):
    """Raised when BAML schema compilation fails."""
    
    def __init__(self, message: str, baml_code: str = None, context: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "baml_compilation", context)
        self.baml_code = baml_code


class LLMProviderError(DynamicBAMLError):
    """Raised when LLM provider call fails."""
    
    def __init__(self, message: str, provider: str = None, context: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "llm_provider", context)
        self.provider = provider


class ResponseParsingError(DynamicBAMLError):
    """Raised when LLM response parsing fails."""
    
    def __init__(self, message: str, raw_response: str = None, schema_name: str = None, context: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "response_parsing", context)
        self.raw_response = raw_response
        self.schema_name = schema_name


class ConfigurationError(DynamicBAMLError):
    """Raised when provider configuration is invalid."""
    
    def __init__(self, message: str, config_key: str = None, context: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "configuration", context)
        self.config_key = config_key


class TimeoutError(DynamicBAMLError):
    """Raised when LLM provider request times out."""
    
    def __init__(self, message: str, timeout_seconds: int = None, context: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "timeout", context)
        self.timeout_seconds = timeout_seconds 