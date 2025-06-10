"""
Tests for the dynamic_baml.baml_executor module.
"""

import json
import pytest
from unittest import TestCase
from unittest.mock import patch, MagicMock

from dynamic_baml.baml_executor import BAMLExecutor, CompiledSchema
from dynamic_baml.exceptions import BAMLCompilationError, ResponseParsingError


class TestBAMLExecutor(TestCase):
    """Test cases for BAMLExecutor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.executor = BAMLExecutor()

    def test_compile_schema_simple(self):
        """Test compiling a simple BAML schema."""
        baml_code = """
        class Person {
            name: string
            age: int
        }
        """
        
        schema = self.executor.compile_schema(baml_code, "Person")
        
        assert isinstance(schema, CompiledSchema)
        assert schema.schema_name == "Person"
        assert schema.baml_code == baml_code
        assert "Person" in schema.parsed_structure
        assert "name" in schema.parsed_structure["Person"]
        assert "age" in schema.parsed_structure["Person"]

    def test_compile_schema_with_enums(self):
        """Test compiling BAML schema with enums."""
        baml_code = """
        enum Status {
            ACTIVE
            INACTIVE
            PENDING
        }
        
        class User {
            name: string
            status: Status
        }
        """
        
        schema = self.executor.compile_schema(baml_code, "User")
        
        assert "Status" in schema.parsed_structure
        assert schema.parsed_structure["Status"]["_type"] == "enum"
        assert "ACTIVE" in schema.parsed_structure["Status"]["values"]

    def test_compile_schema_with_optional_fields(self):
        """Test compiling BAML schema with optional fields."""
        baml_code = """
        class Contact {
            name: string
            email: string?
            phone: string?
        }
        """
        
        schema = self.executor.compile_schema(baml_code, "Contact")
        
        contact_fields = schema.parsed_structure["Contact"]
        assert contact_fields["name"]["optional"] is False
        assert contact_fields["email"]["optional"] is True
        assert contact_fields["phone"]["optional"] is True

    def test_compile_schema_compilation_error(self):
        """Test error handling during schema compilation."""
        # Simulate a compilation error by passing None as baml_code
        with patch.object(self.executor, '_parse_baml_schema', side_effect=Exception("Parse error")):
            with pytest.raises(BAMLCompilationError) as exc_info:
                self.executor.compile_schema("invalid baml", "Test")
            
            assert "Failed to compile BAML schema 'Test'" in str(exc_info.value)
            assert exc_info.value.baml_code == "invalid baml"

    def test_parse_response_with_json(self):
        """Test parsing LLM response with valid JSON."""
        baml_code = """
        class Person {
            name: string
            age: int
        }
        """
        schema = self.executor.compile_schema(baml_code, "Person")
        
        response = '{"name": "John Doe", "age": 30}'
        result = self.executor.parse_response(schema, response, "Person")
        
        assert result == {"name": "John Doe", "age": 30}

    def test_parse_response_with_json_block(self):
        """Test parsing LLM response with JSON inside code block."""
        baml_code = """
        class Person {
            name: string
            age: int
        }
        """
        schema = self.executor.compile_schema(baml_code, "Person")
        
        response = """
        Here's the extracted data:
        ```json
        {"name": "Jane Smith", "age": 25}
        ```
        """
        result = self.executor.parse_response(schema, response, "Person")
        
        assert result == {"name": "Jane Smith", "age": 25}

    def test_parse_response_with_regular_code_block(self):
        """Test parsing LLM response with JSON in regular code block."""
        baml_code = """
        class Person {
            name: string
            age: int
        }
        """
        schema = self.executor.compile_schema(baml_code, "Person")
        
        response = """
        ```
        {"name": "Bob Wilson", "age": 35}
        ```
        """
        result = self.executor.parse_response(schema, response, "Person")
        
        assert result == {"name": "Bob Wilson", "age": 35}

    def test_parse_response_structured_text_fallback(self):
        """Test parsing structured text when no JSON is found."""
        baml_code = """
        class Person {
            name: string
            age: int
        }
        """
        schema = self.executor.compile_schema(baml_code, "Person")
        
        response = """
        name: Alice Cooper
        age: 28
        """
        result = self.executor.parse_response(schema, response, "Person")
        
        assert result["name"] == "Alice Cooper"
        assert result["age"] == "28"

    def test_parse_response_parsing_error(self):
        """Test error handling during response parsing."""
        baml_code = """
        class Person {
            name: string
            age: int
        }
        """
        schema = self.executor.compile_schema(baml_code, "Person")
        
        # Mock the validation to raise an error
        with patch.object(self.executor, '_validate_against_schema', side_effect=Exception("Validation error")):
            with pytest.raises(ResponseParsingError) as exc_info:
                self.executor.parse_response(schema, '{"name": "test"}', "Person")
            
            assert "Failed to parse response for schema 'Person'" in str(exc_info.value)
            assert exc_info.value.raw_response == '{"name": "test"}'
            assert exc_info.value.schema_name == "Person"

    def test_extract_json_from_response_multiple_patterns(self):
        """Test JSON extraction with multiple pattern types."""
        # Test with json code block
        response1 = '```json\n{"key": "value"}\n```'
        result1 = self.executor._extract_json_from_response(response1)
        assert result1 == {"key": "value"}
        
        # Test with regular code block
        response2 = '```\n{"key": "value2"}\n```'
        result2 = self.executor._extract_json_from_response(response2)
        assert result2 == {"key": "value2"}
        
        # Test with inline JSON
        response3 = 'Here is the data: {"key": "value3"} end'
        result3 = self.executor._extract_json_from_response(response3)
        assert result3 == {"key": "value3"}

    def test_extract_json_from_response_no_json(self):
        """Test JSON extraction when no valid JSON is found."""
        response = "This is just plain text with no JSON"
        result = self.executor._extract_json_from_response(response)
        assert result is None

    def test_extract_json_from_response_invalid_json(self):
        """Test JSON extraction with invalid JSON syntax."""
        response = '{"invalid": json}'
        result = self.executor._extract_json_from_response(response)
        assert result is None

    def test_validate_against_schema_non_dict(self):
        """Test schema validation with non-dictionary input."""
        schema = {"test": {"type": "string"}}
        
        with pytest.raises(ValueError, match="Data must be a dictionary"):
            self.executor._validate_against_schema("not a dict", schema)

    def test_parse_structured_text_key_value_pairs(self):
        """Test parsing structured text with key-value pairs."""
        schema = {"name": {"type": "string"}, "age": {"type": "int"}}
        text = """
        name: John Doe
        age: 30
        extra: ignored
        """
        
        result = self.executor._parse_structured_text(text, schema)
        
        assert "name" in result
        assert "age" in result
        assert result["name"] == "John Doe"
        assert result["age"] == "30"

    def test_parse_structured_text_no_colons(self):
        """Test parsing structured text with no key-value pairs."""
        schema = {"test": {"type": "string"}}
        text = "This text has no colons to parse"
        
        result = self.executor._parse_structured_text(text, schema)
        
        assert result == {}

    def test_compiled_schemas_caching(self):
        """Test that compiled schemas are cached properly."""
        baml_code = """
        class Test {
            value: string
        }
        """
        
        schema1 = self.executor.compile_schema(baml_code, "Test")
        schema2 = self.executor.compile_schema(baml_code, "Test")
        
        # Should be cached
        assert "Test" in self.executor.compiled_schemas
        assert self.executor.compiled_schemas["Test"] == schema2


class TestCompiledSchema(TestCase):
    """Test cases for CompiledSchema class."""

    def test_compiled_schema_initialization(self):
        """Test CompiledSchema initialization."""
        schema_name = "TestSchema"
        baml_code = "class TestSchema { value: string }"
        parsed_structure = {"TestSchema": {"value": {"type": "string", "optional": False}}}
        
        schema = CompiledSchema(schema_name, baml_code, parsed_structure)
        
        assert schema.schema_name == schema_name
        assert schema.baml_code == baml_code
        assert schema.parsed_structure == parsed_structure
        assert schema.id is not None
        assert len(schema.id) > 0

    def test_get_main_class_structure(self):
        """Test getting main class structure."""
        schema_name = "Person"
        parsed_structure = {
            "Person": {"name": {"type": "string"}, "age": {"type": "int"}},
            "Address": {"street": {"type": "string"}}
        }
        
        schema = CompiledSchema(schema_name, "", parsed_structure)
        main_structure = schema.get_main_class_structure()
        
        assert main_structure == {"name": {"type": "string"}, "age": {"type": "int"}}

    def test_get_main_class_structure_missing(self):
        """Test getting main class structure when schema name not found."""
        schema_name = "NonExistent"
        parsed_structure = {"Person": {"name": {"type": "string"}}}
        
        schema = CompiledSchema(schema_name, "", parsed_structure)
        main_structure = schema.get_main_class_structure()
        
        assert main_structure == {}

    def test_compiled_schema_unique_ids(self):
        """Test that each CompiledSchema has a unique ID."""
        schema1 = CompiledSchema("Test1", "", {})
        schema2 = CompiledSchema("Test2", "", {})
        
        assert schema1.id != schema2.id 