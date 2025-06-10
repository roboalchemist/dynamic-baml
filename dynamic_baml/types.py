"""
Type definitions for the Dynamic BAML library.
"""

from typing import Any, Dict, List, Literal, Optional, Union
from typing_extensions import TypedDict, NotRequired

# Schema definition types
SchemaFieldType = Union[
    Literal["string", "int", "float", "bool"],
    List[str],  # Array types like ["string"], ["int"]
    Dict[str, Any],  # Nested objects or complex types
]

# Dictionary schema definition
SchemaDict = Dict[str, SchemaFieldType]

# Response data from LLM calls
ResponseData = Dict[str, Any]

# Provider configuration options
class ProviderOptions(TypedDict):
    """Configuration options for LLM providers."""
    provider: Literal["ollama", "openrouter"]
    model: NotRequired[str]
    temperature: NotRequired[float]
    max_tokens: NotRequired[int]
    base_url: NotRequired[str]  # For Ollama
    api_key: NotRequired[str]   # For OpenRouter
    timeout: NotRequired[int]   # Request timeout in seconds

# Enum field definition
class EnumFieldDef(TypedDict):
    """Definition for enum fields in schema."""
    type: Literal["enum"]
    values: List[str]

# Optional field definition  
class OptionalFieldDef(TypedDict):
    """Definition for optional fields in schema."""
    type: str
    optional: Literal[True]
    default: NotRequired[Any]

# Complex schema field types
ComplexSchemaField = Union[
    SchemaFieldType,
    EnumFieldDef,
    OptionalFieldDef,
]

# Extended schema dictionary supporting complex field types
ExtendedSchemaDict = Dict[str, ComplexSchemaField]

# Result type for library calls
class CallResult(TypedDict):
    """Result from call_with_schema function."""
    success: bool
    data: NotRequired[ResponseData]
    error: NotRequired[str]
    error_type: NotRequired[str]

# Internal BAML generation context
class BAMLContext(TypedDict):
    """Internal context for BAML generation."""
    schema_name: str
    schema_code: str
    compiled: bool
    client: NotRequired[Any]  # BAML client instance 