"""
Tests for the dynamic_baml.exceptions module.
"""

import pytest
from unittest import TestCase

from dynamic_baml.exceptions import (
    DynamicBAMLError, LLMProviderError, SchemaGenerationError,
    BAMLCompilationError, ResponseParsingError, ConfigurationError,
    TimeoutError
)


class TestDynamicBAMLError(TestCase):
    """Test cases for DynamicBAMLError base exception class."""

    def test_basic_instantiation(self):
        """Test basic instantiation of DynamicBAMLError."""
        error = DynamicBAMLError("Test error message")
        
        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.error_type == "unknown"
        assert error.context == {}

    def test_instantiation_with_context(self):
        """Test instantiation with additional context information."""
        context = {"provider": "test", "model": "test-model"}
        error = DynamicBAMLError("Test error", "custom_type", context)
        
        assert error.error_type == "custom_type"
        assert error.context == context

    def test_string_representation(self):
        """Test string representation of the error."""
        error = DynamicBAMLError("Custom error message")
        assert str(error) == "Custom error message"

    def test_repr_representation(self):
        """Test repr representation of the error."""
        error = DynamicBAMLError("Test message", "test_type")
        repr_str = repr(error)
        assert "DynamicBAMLError" in repr_str
        assert "Test message" in repr_str

    def test_exception_inheritance(self):
        """Test that DynamicBAMLError inherits from Exception."""
        error = DynamicBAMLError("Test")
        assert isinstance(error, Exception)

    def test_context_is_mutable(self):
        """Test that context dictionary is mutable."""
        error = DynamicBAMLError("Test")
        error.context["new_key"] = "new_value"
        assert error.context["new_key"] == "new_value"


class TestLLMProviderError(TestCase):
    """Test cases for LLMProviderError exception class."""

    def test_basic_instantiation(self):
        """Test basic instantiation of LLMProviderError."""
        error = LLMProviderError("Provider failed", "ollama")
        
        assert str(error) == "Provider failed"
        assert error.message == "Provider failed"
        assert error.error_type == "llm_provider"
        assert error.provider == "ollama"

    def test_instantiation_with_context(self):
        """Test instantiation with additional context."""
        context = {"status_code": 500, "response_time": 30.5}
        error = LLMProviderError("Timeout occurred", "openai", context)
        
        assert error.provider == "openai"
        assert error.context == context

    def test_error_type_is_fixed(self):
        """Test that error_type is always 'llm_provider'."""
        error = LLMProviderError("Test", "test_provider")
        assert error.error_type == "llm_provider"

    def test_inheritance_from_dynamic_baml_error(self):
        """Test that LLMProviderError inherits from DynamicBAMLError."""
        error = LLMProviderError("Test", "provider")
        assert isinstance(error, DynamicBAMLError)
        assert isinstance(error, Exception)

    def test_provider_attribute_accessible(self):
        """Test that provider attribute is accessible."""
        error = LLMProviderError("Test error", "test_provider")
        assert hasattr(error, 'provider')
        assert error.provider == "test_provider"


class TestSchemaGenerationError(TestCase):
    """Test cases for SchemaGenerationError exception class."""

    def test_basic_instantiation(self):
        """Test basic instantiation of SchemaGenerationError."""
        schema = {"name": "string", "age": "int"}
        error = SchemaGenerationError("Invalid schema", schema)
        
        assert str(error) == "Invalid schema"
        assert error.message == "Invalid schema"
        assert error.error_type == "schema_generation"
        assert error.schema_dict == schema

    def test_instantiation_with_context(self):
        """Test instantiation with additional context."""
        schema = {"invalid_field": "unknown_type"}
        context = {"validation_step": "type_check", "field": "invalid_field"}
        error = SchemaGenerationError("Type validation failed", schema, context)
        
        assert error.schema_dict == schema
        assert error.context == context

    def test_error_type_is_fixed(self):
        """Test that error_type is always 'schema_generation'."""
        error = SchemaGenerationError("Test", {})
        assert error.error_type == "schema_generation"

    def test_inheritance_from_dynamic_baml_error(self):
        """Test that SchemaGenerationError inherits from DynamicBAMLError."""
        error = SchemaGenerationError("Test", {})
        assert isinstance(error, DynamicBAMLError)
        assert isinstance(error, Exception)

    def test_schema_dict_attribute_accessible(self):
        """Test that schema_dict attribute is accessible."""
        schema = {"test": "field"}
        error = SchemaGenerationError("Test error", schema)
        assert hasattr(error, 'schema_dict')
        assert error.schema_dict == schema

    def test_empty_schema_dict(self):
        """Test handling of empty schema dictionary."""
        error = SchemaGenerationError("Empty schema", {})
        assert error.schema_dict == {}

    def test_none_schema_dict(self):
        """Test handling of None schema dictionary."""
        error = SchemaGenerationError("Null schema", None)
        assert error.schema_dict is None


class TestBAMLCompilationError(TestCase):
    """Test cases for BAMLCompilationError exception class."""

    def test_basic_instantiation(self):
        """Test basic instantiation of BAMLCompilationError."""
        baml_code = "class Test { field string }"
        error = BAMLCompilationError("Compilation failed", baml_code)
        
        assert str(error) == "Compilation failed"
        assert error.message == "Compilation failed"
        assert error.error_type == "baml_compilation"
        assert error.baml_code == baml_code

    def test_instantiation_with_context(self):
        """Test instantiation with additional context."""
        baml_code = "invalid baml syntax"
        context = {"compiler_version": "1.0.0", "line": 5}
        error = BAMLCompilationError("Syntax error", baml_code, context)
        
        assert error.baml_code == baml_code
        assert error.context == context

    def test_error_type_is_fixed(self):
        """Test that error_type is always 'baml_compilation'."""
        error = BAMLCompilationError("Test", "code")
        assert error.error_type == "baml_compilation"

    def test_inheritance_from_dynamic_baml_error(self):
        """Test that BAMLCompilationError inherits from DynamicBAMLError."""
        error = BAMLCompilationError("Test", "code")
        assert isinstance(error, DynamicBAMLError)
        assert isinstance(error, Exception)

    def test_baml_code_attribute_accessible(self):
        """Test that baml_code attribute is accessible."""
        code = "class Example { name string }"
        error = BAMLCompilationError("Test error", code)
        assert hasattr(error, 'baml_code')
        assert error.baml_code == code

    def test_empty_baml_code(self):
        """Test handling of empty BAML code."""
        error = BAMLCompilationError("Empty code", "")
        assert error.baml_code == ""

    def test_none_baml_code(self):
        """Test handling of None BAML code."""
        error = BAMLCompilationError("Null code", None)
        assert error.baml_code is None


class TestResponseParsingError(TestCase):
    """Test cases for ResponseParsingError exception class."""

    def test_basic_instantiation(self):
        """Test basic instantiation of ResponseParsingError."""
        raw_response = '{"incomplete": json'
        schema_name = "TestSchema"
        error = ResponseParsingError("Parse failed", raw_response, schema_name)
        
        assert str(error) == "Parse failed"
        assert error.message == "Parse failed"
        assert error.error_type == "response_parsing"
        assert error.raw_response == raw_response
        assert error.schema_name == schema_name

    def test_instantiation_with_context(self):
        """Test instantiation with additional context."""
        raw_response = "invalid response"
        schema_name = "Person"
        context = {"parsing_attempt": 2, "fallback_used": True}
        error = ResponseParsingError("Multiple parse failures", raw_response, schema_name, context)
        
        assert error.raw_response == raw_response
        assert error.schema_name == schema_name
        assert error.context == context

    def test_error_type_is_fixed(self):
        """Test that error_type is always 'response_parsing'."""
        error = ResponseParsingError("Test", "response", "schema")
        assert error.error_type == "response_parsing"

    def test_inheritance_from_dynamic_baml_error(self):
        """Test that ResponseParsingError inherits from DynamicBAMLError."""
        error = ResponseParsingError("Test", "response", "schema")
        assert isinstance(error, DynamicBAMLError)
        assert isinstance(error, Exception)

    def test_attributes_accessible(self):
        """Test that all attributes are accessible."""
        error = ResponseParsingError("Test error", "test response", "TestSchema")
        assert hasattr(error, 'raw_response')
        assert hasattr(error, 'schema_name')
        assert error.raw_response == "test response"
        assert error.schema_name == "TestSchema"

    def test_empty_values(self):
        """Test handling of empty values."""
        error = ResponseParsingError("Empty values", "", "")
        assert error.raw_response == ""
        assert error.schema_name == ""

    def test_none_values(self):
        """Test handling of None values."""
        error = ResponseParsingError("Null values", None, None)
        assert error.raw_response is None
        assert error.schema_name is None

    def test_long_response_handling(self):
        """Test handling of very long response text."""
        long_response = "x" * 10000  # Very long string
        error = ResponseParsingError("Long response", long_response, "Schema")
        assert error.raw_response == long_response
        assert len(error.raw_response) == 10000


class TestConfigurationError(TestCase):
    """Test cases for ConfigurationError exception class."""

    def test_basic_instantiation(self):
        """Test basic instantiation of ConfigurationError."""
        error = ConfigurationError("Invalid API key", "api_key")
        
        assert str(error) == "Invalid API key"
        assert error.message == "Invalid API key"
        assert error.error_type == "configuration"
        assert error.config_key == "api_key"

    def test_instantiation_with_context(self):
        """Test instantiation with additional context."""
        context = {"config_file": "settings.json", "line": 15}
        error = ConfigurationError("Missing required field", "model_name", context)
        
        assert error.config_key == "model_name"
        assert error.context == context

    def test_error_type_is_fixed(self):
        """Test that error_type is always 'configuration'."""
        error = ConfigurationError("Test", "test_key")
        assert error.error_type == "configuration"

    def test_inheritance_from_dynamic_baml_error(self):
        """Test that ConfigurationError inherits from DynamicBAMLError."""
        error = ConfigurationError("Test", "key")
        assert isinstance(error, DynamicBAMLError)
        assert isinstance(error, Exception)

    def test_config_key_attribute_accessible(self):
        """Test that config_key attribute is accessible."""
        error = ConfigurationError("Test error", "test_config")
        assert hasattr(error, 'config_key')
        assert error.config_key == "test_config"

    def test_empty_config_key(self):
        """Test handling of empty config key."""
        error = ConfigurationError("Empty key", "")
        assert error.config_key == ""

    def test_none_config_key(self):
        """Test handling of None config key."""
        error = ConfigurationError("Null key", None)
        assert error.config_key is None

    def test_config_validation_scenarios(self):
        """Test various configuration validation scenarios."""
        scenarios = [
            ("Missing API key", "openai_api_key"),
            ("Invalid model name", "model"),
            ("Timeout too large", "timeout_seconds"),
            ("Invalid provider", "provider_type")
        ]
        
        for message, key in scenarios:
            error = ConfigurationError(message, key)
            assert error.config_key == key
            assert error.message == message


class TestTimeoutError(TestCase):
    """Test cases for TimeoutError exception class."""

    def test_basic_instantiation(self):
        """Test basic instantiation of TimeoutError."""
        error = TimeoutError("Request timed out", 30)
        
        assert str(error) == "Request timed out"
        assert error.message == "Request timed out"
        assert error.error_type == "timeout"
        assert error.timeout_seconds == 30

    def test_instantiation_with_context(self):
        """Test instantiation with additional context."""
        context = {"provider": "ollama", "model": "gemma3:1b", "attempt": 3}
        error = TimeoutError("Multiple timeout attempts", 60, context)
        
        assert error.timeout_seconds == 60
        assert error.context == context

    def test_error_type_is_fixed(self):
        """Test that error_type is always 'timeout'."""
        error = TimeoutError("Test", 10)
        assert error.error_type == "timeout"

    def test_inheritance_from_dynamic_baml_error(self):
        """Test that TimeoutError inherits from DynamicBAMLError."""
        error = TimeoutError("Test", 5)
        assert isinstance(error, DynamicBAMLError)
        assert isinstance(error, Exception)

    def test_timeout_seconds_attribute_accessible(self):
        """Test that timeout_seconds attribute is accessible."""
        error = TimeoutError("Test error", 45)
        assert hasattr(error, 'timeout_seconds')
        assert error.timeout_seconds == 45

    def test_zero_timeout(self):
        """Test handling of zero timeout."""
        error = TimeoutError("Zero timeout", 0)
        assert error.timeout_seconds == 0

    def test_none_timeout(self):
        """Test handling of None timeout."""
        error = TimeoutError("Null timeout", None)
        assert error.timeout_seconds is None

    def test_float_timeout(self):
        """Test handling of float timeout values."""
        error = TimeoutError("Float timeout", 30.5)
        assert error.timeout_seconds == 30.5

    def test_timeout_scenarios(self):
        """Test various timeout scenarios."""
        scenarios = [
            ("HTTP request timeout", 30),
            ("LLM generation timeout", 120),
            ("Connection timeout", 5),
            ("Read timeout", 60)
        ]
        
        for message, timeout in scenarios:
            error = TimeoutError(message, timeout)
            assert error.timeout_seconds == timeout
            assert error.message == message


class TestExceptionHierarchy(TestCase):
    """Test cases for exception hierarchy and relationships."""

    def test_all_exceptions_inherit_from_dynamic_baml_error(self):
        """Test that all custom exceptions inherit from DynamicBAMLError."""
        exceptions = [
            LLMProviderError("test", "provider"),
            SchemaGenerationError("test", {}),
            BAMLCompilationError("test", "code"),
            ResponseParsingError("test", "response", "schema"),
            ConfigurationError("test", "key"),
            TimeoutError("test", 30)
        ]
        
        for exc in exceptions:
            assert isinstance(exc, DynamicBAMLError)
            assert isinstance(exc, Exception)

    def test_exception_catching_hierarchy(self):
        """Test that exceptions can be caught by their parent class."""
        try:
            raise LLMProviderError("Test error", "test_provider")
        except DynamicBAMLError as e:
            assert e.message == "Test error"
            assert e.error_type == "llm_provider"

    def test_specific_exception_catching(self):
        """Test that specific exceptions can be caught individually."""
        with pytest.raises(LLMProviderError) as exc_info:
            raise LLMProviderError("Provider failed", "ollama")
        
        assert exc_info.value.provider == "ollama"

    def test_exception_chaining(self):
        """Test exception chaining with 'from' clause."""
        original_error = ValueError("Original error")
        
        try:
            raise LLMProviderError("Provider error", "test") from original_error
        except LLMProviderError as e:
            assert e.__cause__ is original_error

    def test_error_types_are_unique(self):
        """Test that each exception type has a unique error_type."""
        error_types = {
            DynamicBAMLError("test", "custom").error_type,
            LLMProviderError("test", "provider").error_type,
            SchemaGenerationError("test", {}).error_type,
            BAMLCompilationError("test", "code").error_type,
            ResponseParsingError("test", "response", "schema").error_type,
            ConfigurationError("test", "key").error_type,
            TimeoutError("test", 30).error_type
        }
        
        # Should have 7 unique error types (including the custom one)
        assert len(error_types) == 7

    def test_configuration_error_specific_catching(self):
        """Test that ConfigurationError can be caught specifically."""
        with pytest.raises(ConfigurationError) as exc_info:
            raise ConfigurationError("Invalid config", "api_key")
        
        assert exc_info.value.config_key == "api_key"

    def test_timeout_error_specific_catching(self):
        """Test that TimeoutError can be caught specifically."""
        with pytest.raises(TimeoutError) as exc_info:
            raise TimeoutError("Timeout occurred", 30)
        
        assert exc_info.value.timeout_seconds == 30 