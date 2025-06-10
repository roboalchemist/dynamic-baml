"""
Tests for the core Dynamic BAML functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from unittest import TestCase

from dynamic_baml import call_with_schema, call_with_schema_safe
from dynamic_baml.exceptions import (
    DynamicBAMLError,
    SchemaGenerationError,
    LLMProviderError,
    BAMLCompilationError
)


class TestCallWithSchema(TestCase):
    """Test cases for call_with_schema function."""

    @patch('dynamic_baml.core._temporary_baml_project')
    def test_simple_schema_success(self, mock_temp_project):
        """Test successful call with simple schema."""
        schema = {
            "name": "string",
            "age": "int",
            "active": "bool"
        }

        # Mock the BAML project context manager and generated function
        mock_client_module = MagicMock()
        mock_extract_function = MagicMock()
        mock_extract_function.return_value = MagicMock(
            model_dump=lambda: {"name": "John Doe", "age": 30, "active": True}
        )
        mock_client_module.b = MagicMock()
        setattr(mock_client_module.b, 'ExtractDynamicSchema_test1234', mock_extract_function)
        
        mock_temp_project.return_value.__enter__.return_value = ("/tmp/test", mock_client_module)
        mock_temp_project.return_value.__exit__.return_value = None

        with patch('dynamic_baml.core.uuid.uuid4') as mock_uuid:
            mock_uuid.return_value.hex = 'test123456789abc'
            result = call_with_schema(
                "Extract user information",
                schema,
                {"provider": "ollama"}
            )

        assert result == {"name": "John Doe", "age": 30, "active": True}

    @patch('dynamic_baml.core._temporary_baml_project')
    def test_default_options_none(self, mock_temp_project):
        """Test call with None options (should use defaults)."""
        schema = {"name": "string"}

        mock_client_module = MagicMock()
        mock_extract_function = MagicMock()
        mock_extract_function.return_value = MagicMock(
            model_dump=lambda: {"name": "Test User"}
        )
        mock_client_module.b = MagicMock()
        setattr(mock_client_module.b, 'ExtractDynamicSchema_test1234', mock_extract_function)
        
        mock_temp_project.return_value.__enter__.return_value = ("/tmp/test", mock_client_module)
        mock_temp_project.return_value.__exit__.return_value = None

        with patch('dynamic_baml.core.uuid.uuid4') as mock_uuid:
            mock_uuid.return_value.hex = 'test123456789abc'
            result = call_with_schema("Extract user", schema, None)  # None options

        assert result == {"name": "Test User"}

    @patch('dynamic_baml.core._temporary_baml_project')
    def test_openai_provider_config(self, mock_temp_project):
        """Test OpenAI provider configuration."""
        schema = {"message": "string"}

        mock_client_module = MagicMock()
        mock_extract_function = MagicMock()
        mock_extract_function.return_value = MagicMock(
            model_dump=lambda: {"message": "Hello from OpenAI"}
        )
        mock_client_module.b = MagicMock()
        setattr(mock_client_module.b, 'ExtractDynamicSchema_test1234', mock_extract_function)
        
        mock_temp_project.return_value.__enter__.return_value = ("/tmp/test", mock_client_module)
        mock_temp_project.return_value.__exit__.return_value = None

        with patch('dynamic_baml.core.uuid.uuid4') as mock_uuid:
            mock_uuid.return_value.hex = 'test123456789abc'
            result = call_with_schema(
                "Extract message",
                schema,
                {"provider": "openai"}  # This should use MyOpenAI client
            )

        assert result == {"message": "Hello from OpenAI"}

    @patch('dynamic_baml.core._temporary_baml_project')
    def test_anthropic_provider_config(self, mock_temp_project):
        """Test Anthropic provider configuration."""
        schema = {"response": "string"}

        mock_client_module = MagicMock()
        mock_extract_function = MagicMock()
        mock_extract_function.return_value = MagicMock(
            model_dump=lambda: {"response": "Hello from Anthropic"}
        )
        mock_client_module.b = MagicMock()
        setattr(mock_client_module.b, 'ExtractDynamicSchema_test1234', mock_extract_function)
        
        mock_temp_project.return_value.__enter__.return_value = ("/tmp/test", mock_client_module)
        mock_temp_project.return_value.__exit__.return_value = None

        with patch('dynamic_baml.core.uuid.uuid4') as mock_uuid:
            mock_uuid.return_value.hex = 'test123456789abc'
            result = call_with_schema(
                "Extract response",
                schema,
                {"provider": "anthropic"}  # This should use MyAnthropic client
            )

        assert result == {"response": "Hello from Anthropic"}

    @patch('dynamic_baml.core._temporary_baml_project')
    def test_result_with_dict_method(self, mock_temp_project):
        """Test return object that has .dict() method instead of .model_dump()."""
        schema = {"data": "string"}

        mock_client_module = MagicMock()
        mock_extract_function = MagicMock()
        
        # Create a mock result object that has .dict() but not .model_dump()
        mock_result = MagicMock()
        mock_result.dict.return_value = {"data": "Test data"}
        # Remove model_dump to force use of .dict() method
        del mock_result.model_dump
        
        mock_extract_function.return_value = mock_result
        mock_client_module.b = MagicMock()
        setattr(mock_client_module.b, 'ExtractDynamicSchema_test1234', mock_extract_function)
        
        mock_temp_project.return_value.__enter__.return_value = ("/tmp/test", mock_client_module)
        mock_temp_project.return_value.__exit__.return_value = None

        with patch('dynamic_baml.core.uuid.uuid4') as mock_uuid:
            mock_uuid.return_value.hex = 'test123456789abc'
            result = call_with_schema("Extract data", schema)

        assert result == {"data": "Test data"}

    @patch('dynamic_baml.core._temporary_baml_project')
    def test_result_without_methods(self, mock_temp_project):
        """Test return object that has neither .model_dump() nor .dict() methods."""
        schema = {"info": "string"}

        mock_client_module = MagicMock()
        mock_extract_function = MagicMock()
        
        # Create a mock result object that acts like a dict
        mock_result = {"info": "Direct dict conversion"}
        mock_extract_function.return_value = mock_result
        mock_client_module.b = MagicMock()
        setattr(mock_client_module.b, 'ExtractDynamicSchema_test1234', mock_extract_function)
        
        mock_temp_project.return_value.__enter__.return_value = ("/tmp/test", mock_client_module)
        mock_temp_project.return_value.__exit__.return_value = None

        with patch('dynamic_baml.core.uuid.uuid4') as mock_uuid:
            mock_uuid.return_value.hex = 'test123456789abc'
            result = call_with_schema("Extract info", schema)

        assert result == {"info": "Direct dict conversion"}

    @patch('dynamic_baml.core._temporary_baml_project')
    def test_nested_schema_success(self, mock_temp_project):
        """Test successful call with nested schema."""
        schema = {
            "user": {
                "name": "string",
                "email": "string"
            },
            "preferences": {
                "theme": "string",
                "notifications": "bool"
            }
        }

        mock_client_module = MagicMock()
        mock_extract_function = MagicMock()
        mock_extract_function.return_value = MagicMock(
            model_dump=lambda: {
                "user": {"name": "Jane Smith", "email": "jane@example.com"},
                "preferences": {"theme": "dark", "notifications": False}
            }
        )
        mock_client_module.b = MagicMock()
        setattr(mock_client_module.b, 'ExtractDynamicSchema_test1234', mock_extract_function)
        
        mock_temp_project.return_value.__enter__.return_value = ("/tmp/test", mock_client_module)
        mock_temp_project.return_value.__exit__.return_value = None

        with patch('dynamic_baml.core.uuid.uuid4') as mock_uuid:
            mock_uuid.return_value.hex = 'test123456789abc'
            result = call_with_schema(
                "Extract user profile",
                schema,
                {"provider": "ollama"}
            )

        expected = {
            "user": {"name": "Jane Smith", "email": "jane@example.com"},
            "preferences": {"theme": "dark", "notifications": False}
        }
        assert result == expected

    @patch('dynamic_baml.core._temporary_baml_project')
    def test_array_schema_success(self, mock_temp_project):
        """Test successful call with array schema."""
        schema = {
            "items": ["string"],
            "count": "int"
        }

        mock_client_module = MagicMock()
        mock_extract_function = MagicMock()
        mock_extract_function.return_value = MagicMock(
            model_dump=lambda: {"items": ["apple", "banana", "cherry"], "count": 3}
        )
        mock_client_module.b = MagicMock()
        setattr(mock_client_module.b, 'ExtractDynamicSchema_test1234', mock_extract_function)
        
        mock_temp_project.return_value.__enter__.return_value = ("/tmp/test", mock_client_module)
        mock_temp_project.return_value.__exit__.return_value = None

        with patch('dynamic_baml.core.uuid.uuid4') as mock_uuid:
            mock_uuid.return_value.hex = 'test123456789abc'
            result = call_with_schema(
                "Extract shopping list",
                schema,
                {"provider": "ollama"}
            )

        assert result == {"items": ["apple", "banana", "cherry"], "count": 3}

    @patch('dynamic_baml.core._temporary_baml_project')
    def test_enum_schema_success(self, mock_temp_project):
        """Test successful call with enum schema."""
        schema = {
            "status": {
                "type": "enum",
                "values": ["active", "inactive", "pending"]
            },
            "priority": {
                "type": "enum",
                "values": ["low", "medium", "high"]
            }
        }

        mock_client_module = MagicMock()
        mock_extract_function = MagicMock()
        mock_extract_function.return_value = MagicMock(
            model_dump=lambda: {"status": "active", "priority": "high"}
        )
        mock_client_module.b = MagicMock()
        setattr(mock_client_module.b, 'ExtractDynamicSchema_test1234', mock_extract_function)
        
        mock_temp_project.return_value.__enter__.return_value = ("/tmp/test", mock_client_module)
        mock_temp_project.return_value.__exit__.return_value = None

        with patch('dynamic_baml.core.uuid.uuid4') as mock_uuid:
            mock_uuid.return_value.hex = 'test123456789abc'
            result = call_with_schema(
                "Extract status information",
                schema,
                {"provider": "ollama"}
            )

        assert result == {"status": "active", "priority": "high"}

    @patch('dynamic_baml.core._temporary_baml_project')
    def test_optional_fields_schema(self, mock_temp_project):
        """Test schema with optional fields."""
        schema = {
            "name": "string",
            "email": {"type": "string", "optional": True},
            "phone": {"type": "string", "optional": True}
        }

        mock_client_module = MagicMock()
        mock_extract_function = MagicMock()
        mock_extract_function.return_value = MagicMock(
            model_dump=lambda: {"name": "Bob Wilson", "email": "bob@example.com"}
        )
        mock_client_module.b = MagicMock()
        setattr(mock_client_module.b, 'ExtractDynamicSchema_test1234', mock_extract_function)
        
        mock_temp_project.return_value.__enter__.return_value = ("/tmp/test", mock_client_module)
        mock_temp_project.return_value.__exit__.return_value = None

        with patch('dynamic_baml.core.uuid.uuid4') as mock_uuid:
            mock_uuid.return_value.hex = 'test123456789abc'
            result = call_with_schema(
                "Extract contact info",
                schema,
                {"provider": "ollama"}
            )

        assert result == {"name": "Bob Wilson", "email": "bob@example.com"}

    @patch('dynamic_baml.core._temporary_baml_project')
    def test_provider_error_handling(self, mock_temp_project):
        """Test proper error handling for provider failures."""
        schema = {"name": "string"}

        # Mock BAML client that raises an exception
        mock_client_module = MagicMock()
        mock_extract_function = MagicMock()
        mock_extract_function.side_effect = Exception("BAML execution error")
        mock_client_module.b = MagicMock()
        setattr(mock_client_module.b, 'ExtractDynamicSchema_test1234', mock_extract_function)
        
        mock_temp_project.return_value.__enter__.return_value = ("/tmp/test", mock_client_module)
        mock_temp_project.return_value.__exit__.return_value = None

        with patch('dynamic_baml.core.uuid.uuid4') as mock_uuid:
            mock_uuid.return_value.hex = 'test123456789abc'
            with pytest.raises(DynamicBAMLError) as exc_info:
                call_with_schema(
                    "Extract user information",
                    schema,
                    {"provider": "ollama"}
                )
        
        assert "Unexpected error: BAML execution error" in str(exc_info.value)

    @patch('dynamic_baml.core._temporary_baml_project')
    def test_dynamic_baml_error_passthrough(self, mock_temp_project):
        """Test that DynamicBAMLError exceptions are passed through without wrapping."""
        schema = {"name": "string"}

        # Mock BAML client that raises a DynamicBAMLError
        mock_client_module = MagicMock()
        mock_extract_function = MagicMock()
        original_error = LLMProviderError("Provider timeout", "ollama")
        mock_extract_function.side_effect = original_error
        mock_client_module.b = MagicMock()
        setattr(mock_client_module.b, 'ExtractDynamicSchema_test1234', mock_extract_function)
        
        mock_temp_project.return_value.__enter__.return_value = ("/tmp/test", mock_client_module)
        mock_temp_project.return_value.__exit__.return_value = None

        with patch('dynamic_baml.core.uuid.uuid4') as mock_uuid:
            mock_uuid.return_value.hex = 'test123456789abc'
            with pytest.raises(LLMProviderError) as exc_info:
                call_with_schema("Extract user", schema)
        
        # Should be the original error, not wrapped
        assert exc_info.value is original_error

    @patch('dynamic_baml.core._temporary_baml_project')
    def test_openrouter_provider(self, mock_temp_project):
        """Test OpenRouter provider configuration."""
        schema = {"content": "string"}

        mock_client_module = MagicMock()
        mock_extract_function = MagicMock()
        mock_extract_function.return_value = MagicMock(
            model_dump=lambda: {"content": "OpenRouter response"}
        )
        mock_client_module.b = MagicMock()
        setattr(mock_client_module.b, 'ExtractDynamicSchema_test1234', mock_extract_function)
        
        mock_temp_project.return_value.__enter__.return_value = ("/tmp/test", mock_client_module)
        mock_temp_project.return_value.__exit__.return_value = None

        with patch('dynamic_baml.core.uuid.uuid4') as mock_uuid:
            mock_uuid.return_value.hex = 'test123456789abc'
            result = call_with_schema(
                "Extract content",
                schema,
                {"provider": "openrouter"}
            )

        assert result == {"content": "OpenRouter response"}

    @patch('dynamic_baml.core._temporary_baml_project')
    def test_empty_schema_dict(self, mock_temp_project):
        """Test handling of empty schema dictionary (should work gracefully)."""
        mock_client_module = MagicMock()
        mock_extract_function = MagicMock()
        mock_extract_function.return_value = MagicMock(
            model_dump=lambda: {}
        )
        mock_client_module.b = MagicMock()
        setattr(mock_client_module.b, 'ExtractDynamicSchema_test1234', mock_extract_function)
        
        mock_temp_project.return_value.__enter__.return_value = ("/tmp/test", mock_client_module)
        mock_temp_project.return_value.__exit__.return_value = None

        with patch('dynamic_baml.core.uuid.uuid4') as mock_uuid:
            mock_uuid.return_value.hex = 'test123456789abc'
            result = call_with_schema(
                "Test prompt",
                {},
                {"provider": "ollama"}
            )
        
        # Empty schema should return empty dict
        assert result == {}


class TestCallWithSchemaSafe(TestCase):
    """Test cases for call_with_schema_safe function."""

    @patch('dynamic_baml.core._temporary_baml_project')
    def test_safe_success(self, mock_temp_project):
        """Test successful safe call."""
        schema = {"message": "string"}

        mock_client_module = MagicMock()
        mock_extract_function = MagicMock()
        mock_extract_function.return_value = MagicMock(
            model_dump=lambda: {"message": "Success"}
        )
        mock_client_module.b = MagicMock()
        setattr(mock_client_module.b, 'ExtractDynamicSchema_test1234', mock_extract_function)
        
        mock_temp_project.return_value.__enter__.return_value = ("/tmp/test", mock_client_module)
        mock_temp_project.return_value.__exit__.return_value = None

        with patch('dynamic_baml.core.uuid.uuid4') as mock_uuid:
            mock_uuid.return_value.hex = 'test123456789abc'
            result = call_with_schema_safe("Test prompt", schema)

        assert result["success"] is True
        assert result["data"] == {"message": "Success"}

    @patch('dynamic_baml.core._temporary_baml_project')
    def test_safe_error_handling(self, mock_temp_project):
        """Test safe error handling returns structured error."""
        schema = {"name": "string"}

        mock_client_module = MagicMock()
        mock_extract_function = MagicMock()
        mock_extract_function.side_effect = LLMProviderError("Provider failed", "ollama")
        mock_client_module.b = MagicMock()
        setattr(mock_client_module.b, 'ExtractDynamicSchema_test1234', mock_extract_function)
        
        mock_temp_project.return_value.__enter__.return_value = ("/tmp/test", mock_client_module)
        mock_temp_project.return_value.__exit__.return_value = None

        with patch('dynamic_baml.core.uuid.uuid4') as mock_uuid:
            mock_uuid.return_value.hex = 'test123456789abc'
            result = call_with_schema_safe("Test prompt", schema)

        assert result["success"] is False
        assert result["error"] == "Provider failed"
        assert result["error_type"] == "llm_provider"

    @patch('dynamic_baml.core._temporary_baml_project')
    def test_safe_non_dynamic_baml_error_handling(self, mock_temp_project):
        """Test safe handling of non-DynamicBAMLError exceptions."""
        schema = {"data": "string"}

        mock_client_module = MagicMock()
        mock_extract_function = MagicMock()
        mock_extract_function.side_effect = ValueError("Unexpected error")
        mock_client_module.b = MagicMock()
        setattr(mock_client_module.b, 'ExtractDynamicSchema_test1234', mock_extract_function)
        
        mock_temp_project.return_value.__enter__.return_value = ("/tmp/test", mock_client_module)
        mock_temp_project.return_value.__exit__.return_value = None

        with patch('dynamic_baml.core.uuid.uuid4') as mock_uuid:
            mock_uuid.return_value.hex = 'test123456789abc'
            result = call_with_schema_safe("Test prompt", schema)

        assert result["success"] is False
        assert "Unexpected error" in result["error"]
        assert result["error_type"] == "unknown"


class TestTemporaryBAMLProject(TestCase):
    """Test cases for _TemporaryBAMLProject functionality."""

    @patch('dynamic_baml.core.subprocess.run')
    @patch('dynamic_baml.core.tempfile.mkdtemp')
    @patch('dynamic_baml.core.shutil.rmtree')
    def test_baml_compilation_error(self, mock_rmtree, mock_mkdtemp, mock_subprocess):
        """Test BAMLCompilationError is raised when baml-cli fails."""
        from dynamic_baml.core import _TemporaryBAMLProject
        from pathlib import Path
        
        # Setup mocks
        temp_dir = "/tmp/test_baml_project"
        mock_mkdtemp.return_value = temp_dir
        
        # Mock failed subprocess call
        mock_subprocess.return_value.returncode = 1
        mock_subprocess.return_value.stdout = "Compilation failed"
        mock_subprocess.return_value.stderr = "Syntax error in BAML"
        
        # Mock Path to prevent actual file operations
        with patch('dynamic_baml.core.Path') as mock_path_class:
            mock_project_dir = MagicMock()
            mock_baml_src_dir = MagicMock()
            mock_project_dir.__truediv__.return_value = mock_baml_src_dir
            mock_path_class.return_value = mock_project_dir
            
            project = _TemporaryBAMLProject("invalid baml code", "TestFunction")
            
            with pytest.raises(BAMLCompilationError) as exc_info:
                with project:
                    pass
            
            assert "BAML generation failed" in str(exc_info.value)
            assert exc_info.value.baml_code == "invalid baml code"
            # Verify cleanup was called
            mock_rmtree.assert_called()

    @patch('dynamic_baml.core.subprocess.run')
    @patch('dynamic_baml.core.tempfile.mkdtemp')
    @patch('dynamic_baml.core.shutil.rmtree')
    def test_client_directory_not_found_error(self, mock_rmtree, mock_mkdtemp, mock_subprocess):
        """Test BAMLCompilationError when generated client directory is missing."""
        from dynamic_baml.core import _TemporaryBAMLProject
        from pathlib import Path
        
        # Setup mocks
        temp_dir = "/tmp/test_baml_project"
        mock_mkdtemp.return_value = temp_dir
        
        # Mock successful subprocess call
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = "Generation successful"
        mock_subprocess.return_value.stderr = ""
        
        # Mock Path to return a path that has a client dir that doesn't exist
        with patch('dynamic_baml.core.Path') as mock_path_class:
            mock_project_dir = MagicMock()
            mock_baml_src_dir = MagicMock()
            mock_client_dir = MagicMock()
            mock_client_dir.exists.return_value = False  # Client dir doesn't exist
            
            mock_project_dir.__truediv__.side_effect = lambda x: {
                "baml_src": mock_baml_src_dir,
                "baml_client": mock_client_dir
            }[x]
            mock_path_class.return_value = mock_project_dir
            
            project = _TemporaryBAMLProject("valid baml code", "TestFunction")
            
            with pytest.raises(BAMLCompilationError) as exc_info:
                with project:
                    pass
            
            assert "Generated baml_client directory not found" in str(exc_info.value)

    @patch('dynamic_baml.core.subprocess.run')
    @patch('dynamic_baml.core.tempfile.mkdtemp')
    @patch('dynamic_baml.core.shutil.rmtree')
    @patch('dynamic_baml.core.sys')
    def test_import_error_handling(self, mock_sys, mock_rmtree, mock_mkdtemp, mock_subprocess):
        """Test BAMLCompilationError when client import fails."""
        from dynamic_baml.core import _TemporaryBAMLProject
        from pathlib import Path
        
        # Setup mocks
        temp_dir = "/tmp/test_baml_project"
        mock_mkdtemp.return_value = temp_dir
        
        # Mock successful subprocess call
        mock_subprocess.return_value.returncode = 0
        
        # Mock Path to simulate existing client directory
        with patch('dynamic_baml.core.Path') as mock_path_class:
            mock_project_dir = MagicMock()
            mock_baml_src_dir = MagicMock()
            mock_client_dir = MagicMock()
            mock_client_dir.exists.return_value = True  # Client dir exists
            
            mock_project_dir.__truediv__.side_effect = lambda x: {
                "baml_src": mock_baml_src_dir,
                "baml_client": mock_client_dir
            }[x]
            mock_path_class.return_value = mock_project_dir
            
            # Mock import failure
            with patch('builtins.__import__', side_effect=ImportError("Cannot import client")):
                project = _TemporaryBAMLProject("valid baml code", "TestFunction")
                
                with pytest.raises(BAMLCompilationError) as exc_info:
                    with project:
                        pass
                
                assert "Failed to import generated client" in str(exc_info.value)


class TestSchemaGeneration(TestCase):
    """Test cases for schema generation edge cases."""

    def test_invalid_schema_dict(self):
        """Test error handling for invalid schema dictionary."""
        with pytest.raises(DynamicBAMLError):
            call_with_schema(
                "Test prompt",
                "not a dictionary",
                {"provider": "ollama"}
            )

    def test_simple_schema_generation(self):
        """Test basic schema generation without actual BAML compilation."""
        from dynamic_baml.schema_generator import DictToBAMLGenerator
        
        schema_dict = {
            "name": "string",
            "age": "int",
            "active": "bool"
        }
        
        generator = DictToBAMLGenerator()
        baml_code = generator.generate_schema(schema_dict, "TestSchema")
        
        assert "class TestSchema {" in baml_code
        assert "name string" in baml_code
        assert "age int" in baml_code
        assert "active bool" in baml_code

    def test_nested_schema_generation(self):
        """Test nested schema generation."""
        from dynamic_baml.schema_generator import DictToBAMLGenerator
        
        schema_dict = {
            "user": {
                "name": "string",
                "email": "string"
            },
            "settings": {
                "theme": "string",
                "notifications": "bool"
            }
        }
        
        generator = DictToBAMLGenerator()
        baml_code = generator.generate_schema(schema_dict, "UserProfile")
        
        assert "class UserProfile {" in baml_code
        assert "class UserClass {" in baml_code
        assert "class SettingsClass {" in baml_code

    def test_enum_schema_generation(self):
        """Test enum schema generation."""
        from dynamic_baml.schema_generator import DictToBAMLGenerator
        
        schema_dict = {
            "status": {
                "type": "enum",
                "values": ["active", "inactive", "pending"]
            }
        }
        
        generator = DictToBAMLGenerator()
        baml_code = generator.generate_schema(schema_dict, "StatusInfo")
        
        assert "enum StatusEnum {" in baml_code
        # Schema generator converts enum values to uppercase
        assert "ACTIVE" in baml_code
        assert "INACTIVE" in baml_code
        assert "PENDING" in baml_code

    def test_optional_fields_generation(self):
        """Test optional fields in schema generation."""
        from dynamic_baml.schema_generator import DictToBAMLGenerator
        
        schema_dict = {
            "name": "string",
            "email": {"type": "string", "optional": True},
            "phone": {"type": "string", "optional": True}
        }
        
        generator = DictToBAMLGenerator()
        baml_code = generator.generate_schema(schema_dict, "ContactInfo")
        
        assert "class ContactInfo {" in baml_code
        assert "name string" in baml_code
        assert "email string?" in baml_code
        assert "phone string?" in baml_code 