"""
Dynamic BAML Library

A standalone library for dynamic BoundaryML schema generation and LLM response parsing.
"""

from .core import call_with_schema, call_with_schema_safe
from .exceptions import (
    DynamicBAMLError,
    SchemaGenerationError,
    BAMLCompilationError,
    LLMProviderError,
    ResponseParsingError,
)
from .types import SchemaDict, ResponseData, ProviderOptions

__version__ = "0.1.0"
__all__ = [
    # Main interface
    "call_with_schema",
    "call_with_schema_safe",
    
    # Exception types
    "DynamicBAMLError",
    "SchemaGenerationError", 
    "BAMLCompilationError",
    "LLMProviderError",
    "ResponseParsingError",
    
    # Type definitions
    "SchemaDict",
    "ResponseData",
    "ProviderOptions",
] 