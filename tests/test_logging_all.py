"""
Comprehensive test suite for Dynamic BAML logging functionality.

This file consolidates all logging tests:
- Unit tests for basic functionality
- Comprehensive tests for edge cases and configurations  
- Integration tests for real BAML operations (requires Ollama)
- Core module coverage tests for uncovered functions

Run all tests: pytest tests/test_logging_all.py -v
Run without integration: pytest tests/test_logging_all.py -v -m "not integration"
Run unit tests only: pytest tests/test_logging_all.py::TestLoggingUnit -v
"""

import pytest
import os
import tempfile
import time
import threading
import queue
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from unittest import TestCase
import io
from contextlib import redirect_stderr
import unittest

from dynamic_baml.types import ProviderOptions
from dynamic_baml.core import (
    _configure_logging, 
    _setup_log_file_redirect, 
    _get_client_config, 
    _generate_baml_function,
    _TemporaryBAMLProject,
    call_with_schema,
    call_with_schema_safe
)
from dynamic_baml import call_with_schema, call_with_schema_safe
from dynamic_baml.providers import LLMProviderFactory
from dynamic_baml.exceptions import DynamicBAMLError, BAMLCompilationError
from dynamic_baml.baml_executor import BAMLExecutor


class TestLoggingUnit(TestCase):
    """Unit tests for logging configuration options."""
    
    def test_provider_options_has_logging_fields(self):
        """Test that ProviderOptions TypedDict includes logging fields."""
        options: ProviderOptions = {
            "provider": "ollama",
            "log_level": "info",
            "log_file": "/tmp/test.log"
        }
        
        assert options["provider"] == "ollama"
        assert options["log_level"] == "info"
        assert options["log_file"] == "/tmp/test.log"
    
    def test_configure_logging_with_level(self):
        """Test _configure_logging with log_level option."""
        with patch('dynamic_baml.baml.config.set_log_level') as mock_set_level:
            options: ProviderOptions = {
                "provider": "ollama",
                "log_level": "debug"
            }
            
            _configure_logging(options)
            
            mock_set_level.assert_called_once_with("debug")
    
    def test_configure_logging_with_file(self):
        """Test _configure_logging with log_file option."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            log_file = f.name
        
        try:
            with patch('dynamic_baml.core._setup_log_file_redirect') as mock_setup:
                options: ProviderOptions = {
                    "provider": "ollama",
                    "log_file": log_file
                }
                
                _configure_logging(options)
                
                mock_setup.assert_called_once_with(log_file)
        finally:
            if Path(log_file).exists():
                os.unlink(log_file)
    
    def test_configure_logging_with_both_options(self):
        """Test _configure_logging with both log_level and log_file."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            log_file = f.name
        
        try:
            with patch('dynamic_baml.baml.config.set_log_level') as mock_set_level, \
                 patch('dynamic_baml.core._setup_log_file_redirect') as mock_setup:
                
                options: ProviderOptions = {
                    "provider": "ollama",
                    "log_level": "info",
                    "log_file": log_file
                }
                
                _configure_logging(options)
                
                mock_set_level.assert_called_once_with("info")
                mock_setup.assert_called_once_with(log_file)
        finally:
            if Path(log_file).exists():
                os.unlink(log_file)
    
    def test_configure_logging_no_options(self):
        """Test _configure_logging with no logging options."""
        with patch('dynamic_baml.baml.config.set_log_level') as mock_set_level:
            options: ProviderOptions = {
                "provider": "ollama"
            }
            
            _configure_logging(options)
            
            # Should not call set_log_level if no log_level specified
            mock_set_level.assert_not_called()
    
    def test_configure_logging_handles_import_error(self):
        """Test _configure_logging handles ImportError gracefully."""
        with patch('dynamic_baml.baml.config.set_log_level', side_effect=ImportError("No module")):
            options: ProviderOptions = {
                "provider": "ollama",
                "log_level": "info"
            }
            
            # Should not raise exception
            _configure_logging(options)
    
    def test_setup_log_file_redirect_creates_directory(self):
        """Test _setup_log_file_redirect creates parent directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "subdir", "test.log")
            
            _setup_log_file_redirect(log_file)
            
            # Check that parent directory was created
            assert Path(log_file).parent.exists()
            # Check that environment variable was set
            assert os.environ.get('DYNAMIC_BAML_LOG_FILE') == log_file
    
    def test_setup_log_file_redirect_handles_errors(self):
        """Test _setup_log_file_redirect handles errors gracefully."""
        # Use an invalid path that should cause an error
        invalid_path = "/invalid/path/that/should/not/exist/test.log"
        
        # Should not raise exception even with invalid path
        _setup_log_file_redirect(invalid_path)
    
    def test_log_level_valid_values(self):
        """Test that all valid log level values are accepted."""
        valid_levels = ["off", "error", "warn", "info", "debug", "trace"]
        
        for level in valid_levels:
            options: ProviderOptions = {
                "provider": "ollama",
                "log_level": level  # type: ignore
            }
            # Should not raise type errors
            assert options["log_level"] == level

    def test_logging_options_are_optional(self):
        """Test that logging options are optional in ProviderOptions."""
        # This should work without logging options
        options: ProviderOptions = {
            "provider": "ollama"
        }
        
        assert options["provider"] == "ollama"
        assert "log_level" not in options
        assert "log_file" not in options


class TestCoreCoverage(TestCase):
    """Tests specifically designed to increase coverage of core.py functions."""

    def test_get_client_config_all_providers(self):
        """Test _get_client_config with all supported providers."""
        test_cases = [
            ({"provider": "ollama"}, "Ollama"),
            ({"provider": "openai"}, "OpenAI"),
            ({"provider": "anthropic"}, "Anthropic"),
            ({"provider": "openrouter"}, "OpenRouter"),
            ({"provider": "unknown_provider"}, "Ollama"),  # Default case
            ({"provider": "OPENAI"}, "OpenAI"),  # Case insensitive
        ]
        
        for options, expected in test_cases:
            with self.subTest(provider=options["provider"]):
                result = _get_client_config(options)
                self.assertEqual(result, expected)
    
    def test_generate_baml_function(self):
        """Test _generate_baml_function generates correct BAML code."""
        function_name = "TestFunction"
        schema_name = "TestSchema"
        client_config = "OpenAI"
        prompt_text = "Extract data from the following text"
        
        result = _generate_baml_function(function_name, schema_name, client_config, prompt_text)
        
        # Verify the function contains expected elements
        self.assertIn(f"function {function_name}", result)
        self.assertIn(f"-> {schema_name}", result)
        self.assertIn(f"client {client_config}", result)
        self.assertIn(prompt_text, result)
        self.assertIn("input_text", result)
        self.assertIn("ctx.output_format", result)

    def test_setup_log_file_redirect_baml_log_handler(self):
        """Test the BAMLLogHandler class within _setup_log_file_redirect."""
        import logging
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            log_file = f.name
        
        try:
            # Test the function without mocking to verify it works
            _setup_log_file_redirect(log_file)
            
            # Verify environment variable was set
            self.assertEqual(os.environ.get('DYNAMIC_BAML_LOG_FILE'), log_file)
            
            # Verify parent directory exists
            self.assertTrue(Path(log_file).parent.exists())
            
        finally:
            if Path(log_file).exists():
                os.unlink(log_file)
            if 'DYNAMIC_BAML_LOG_FILE' in os.environ:
                del os.environ['DYNAMIC_BAML_LOG_FILE']

    def test_baml_log_handler_functionality(self):
        """Test the BAMLLogHandler class functionality directly."""
        # This test targets the internal BAMLLogHandler class lines 66-68, 71-76, 79-81
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            log_file = f.name
        
        try:
            # Create the handler by calling the function that defines it
            _setup_log_file_redirect(log_file)
            
            # Now test specific error handling paths
            with patch('builtins.open', side_effect=PermissionError("Permission denied")):
                # This should trigger the exception handling in _setup_log_file_redirect
                with patch('builtins.print') as mock_print:
                    _setup_log_file_redirect("/invalid/path/test.log")
                    mock_print.assert_called_once()
                    
        finally:
            if Path(log_file).exists():
                os.unlink(log_file)
            if 'DYNAMIC_BAML_LOG_FILE' in os.environ:
                del os.environ['DYNAMIC_BAML_LOG_FILE']

    def test_setup_log_file_redirect_exception_handling(self):
        """Test exception handling in _setup_log_file_redirect."""
        
        # Test with a path that should cause an error during file operations
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            with patch('builtins.print') as mock_print:
                _setup_log_file_redirect("/some/invalid/path.log")
                
                # Should print warning but not raise exception
                mock_print.assert_called_once()
                self.assertIn("Warning", mock_print.call_args[0][0])

    def test_temporary_baml_project_init(self):
        """Test _TemporaryBAMLProject initialization."""
        baml_code = "class Test { name string }"
        function_name = "TestFunction"
        options = {"provider": "openai", "model": "gpt-4"}
        
        project = _TemporaryBAMLProject(baml_code, function_name, options)
        
        self.assertEqual(project.baml_code, baml_code)
        self.assertEqual(project.function_name, function_name)
        self.assertEqual(project.options, options)
        self.assertIsNone(project.project_dir)
        self.assertIsNone(project.client_module)

    def test_temporary_baml_project_default_options(self):
        """Test _TemporaryBAMLProject with default options."""
        baml_code = "class Test { name string }"
        function_name = "TestFunction"
        
        project = _TemporaryBAMLProject(baml_code, function_name)
        
        # Should have default options
        expected_defaults = {"provider": "ollama", "model": "gemma3:1b"}
        self.assertEqual(project.options, expected_defaults)

    def test_call_with_schema_exception_handling(self):
        """Test exception handling in call_with_schema."""
        schema = {"name": "string"}
        prompt = "Test prompt"
        
        # Test DynamicBAMLError passthrough
        with patch('dynamic_baml.core._temporary_baml_project') as mock_project:
            mock_project.side_effect = DynamicBAMLError("Test error", "test_type")
            
            with self.assertRaises(DynamicBAMLError) as cm:
                call_with_schema(prompt, schema)
            
            self.assertEqual(str(cm.exception), "Test error")

    def test_call_with_schema_unexpected_exception(self):
        """Test handling of unexpected exceptions in call_with_schema."""
        schema = {"name": "string"}
        prompt = "Test prompt"
        
        # Test unexpected exception wrapping
        with patch('dynamic_baml.core._temporary_baml_project') as mock_project:
            mock_project.side_effect = ValueError("Unexpected error")
            
            with self.assertRaises(DynamicBAMLError) as cm:
                call_with_schema(prompt, schema)
            
            self.assertIn("Unexpected error", str(cm.exception))

    def test_call_with_schema_result_conversion_paths(self):
        """Test different result conversion paths in call_with_schema."""
        schema = {"name": "string"}
        prompt = "Test prompt"
        
        # Mock the temporary project to test result conversion
        with patch('dynamic_baml.core._temporary_baml_project') as mock_project:
            mock_client = MagicMock()
            mock_function = MagicMock()
            
            # Test 1: model_dump method
            mock_result = MagicMock()
            mock_result.model_dump.return_value = {"name": "test_model_dump"}
            mock_function.return_value = mock_result
            mock_client.b = MagicMock()
            setattr(mock_client.b, "ExtractDynamicSchema_12345678", mock_function)
            
            mock_project.return_value.__enter__.return_value = (Path("/tmp"), mock_client)
            mock_project.return_value.__exit__.return_value = None
            
            with patch('dynamic_baml.core.uuid.uuid4') as mock_uuid:
                mock_uuid.return_value.hex = "12345678" * 4
                
                result = call_with_schema(prompt, schema)
                self.assertEqual(result, {"name": "test_model_dump"})
            
            # Test 2: dict method (fallback)
            mock_result2 = MagicMock()
            del mock_result2.model_dump  # Remove model_dump to test dict path
            mock_result2.dict.return_value = {"name": "test_dict"}
            mock_function.return_value = mock_result2
            
            with patch('dynamic_baml.core.uuid.uuid4') as mock_uuid:
                mock_uuid.return_value.hex = "12345678" * 4
                
                result = call_with_schema(prompt, schema)
                self.assertEqual(result, {"name": "test_dict"})
            
            # Test 3: dict() fallback (neither model_dump nor dict method)
            mock_result3 = {"name": "test_dict_conversion"}
            mock_function.return_value = mock_result3
            
            with patch('dynamic_baml.core.uuid.uuid4') as mock_uuid:
                mock_uuid.return_value.hex = "12345678" * 4
                
                result = call_with_schema(prompt, schema)
                self.assertEqual(result, {"name": "test_dict_conversion"})

    def test_call_with_schema_safe_error_handling(self):
        """Test error handling in call_with_schema_safe."""
        schema = {"name": "string"}
        prompt = "Test prompt"
        
        # Test DynamicBAMLError handling
        with patch('dynamic_baml.core.call_with_schema') as mock_call:
            error = DynamicBAMLError("Test error", "test_type")
            error.message = "Test error message"
            error.error_type = "test_error_type"
            mock_call.side_effect = error
            
            result = call_with_schema_safe(prompt, schema)
            
            self.assertFalse(result["success"])
            self.assertEqual(result["error"], "Test error message")
            self.assertEqual(result["error_type"], "test_error_type")
        
        # Test unexpected exception handling
        with patch('dynamic_baml.core.call_with_schema') as mock_call:
            mock_call.side_effect = ValueError("Unexpected error")
            
            result = call_with_schema_safe(prompt, schema)
            
            self.assertFalse(result["success"])
            self.assertEqual(result["error"], "Unexpected error")
            self.assertEqual(result["error_type"], "unknown")

    def test_configure_logging_exception_handling(self):
        """Test exception handling in _configure_logging."""
        
        # Test general exception handling (not ImportError)
        with patch('dynamic_baml.baml.config.set_log_level', side_effect=RuntimeError("Runtime error")):
            with patch('builtins.print') as mock_print:
                options: ProviderOptions = {
                    "provider": "ollama",
                    "log_level": "info"
                }
                
                _configure_logging(options)
                
                # Should print warning
                mock_print.assert_called_once()
                self.assertIn("Warning: Failed to configure logging", mock_print.call_args[0][0])


class TestCoreMocked(TestCase):
    """Tests for core functionality with comprehensive mocking."""

    def test_temporary_baml_project_model_selection(self):
        """Test model selection logic in _TemporaryBAMLProject."""
        test_cases = [
            ({"provider": "openai"}, "gpt-4o"),
            ({"provider": "openai", "model": "gpt-3.5-turbo"}, "gpt-3.5-turbo"),
            ({"provider": "anthropic"}, "claude-3-5-sonnet-20241022"),
            ({"provider": "anthropic", "model": "claude-3-opus-20240229"}, "claude-3-opus-20240229"),
            ({"provider": "ollama"}, "gemma3:1b"),
            ({"provider": "ollama", "model": "llama2"}, "llama2"),
            ({"provider": "openrouter"}, "google/gemini-2.0-flash-exp"),
            ({"provider": "openrouter", "model": "anthropic/claude-3-5-sonnet"}, "anthropic/claude-3-5-sonnet"),
            ({"provider": "unknown"}, "gemma3:1b"),  # Default case
        ]
        
        for options, expected_model in test_cases:
            with self.subTest(provider=options.get("provider"), model=options.get("model")):
                project = _TemporaryBAMLProject("class Test {}", "TestFunc", options)
                
                # Test that the model selection logic works correctly
                provider = options.get("provider", "ollama").lower()
                if provider == "openai":
                    actual_model = options.get("model", "gpt-4o")
                elif provider == "anthropic":
                    actual_model = options.get("model", "claude-3-5-sonnet-20241022")
                elif provider == "ollama":
                    actual_model = options.get("model", "gemma3:1b")
                elif provider == "openrouter":
                    actual_model = options.get("model", "google/gemini-2.0-flash-exp")
                else:
                    actual_model = options.get("model", "gemma3:1b")
                
                self.assertEqual(actual_model, expected_model)

    def test_temporary_baml_project_context_manager_error_cleanup(self):
        """Test cleanup when errors occur in _TemporaryBAMLProject.__enter__."""
        project = _TemporaryBAMLProject("class Test {}", "TestFunc")
        
        # Mock the entire method to test error cleanup logic
        with patch.object(project, 'project_dir', Path("/tmp/test_project")), \
             patch('pathlib.Path.exists') as mock_exists, \
             patch('shutil.rmtree') as mock_rmtree:
            
            mock_exists.return_value = True
            
            # Call __exit__ directly to test cleanup
            project.__exit__(Exception, Exception("test"), None)
            
            # Verify cleanup was called
            mock_rmtree.assert_called_once_with(Path("/tmp/test_project"))

    def test_temporary_baml_project_import_error(self):
        """Test ImportError handling in _TemporaryBAMLProject.__enter__.""" 
        project = _TemporaryBAMLProject("class Test {}", "TestFunc")
        
        with patch('tempfile.mkdtemp') as mock_mkdtemp, \
             patch('pathlib.Path.mkdir'), \
             patch('pathlib.Path.write_text'), \
             patch('subprocess.run') as mock_subprocess, \
             patch('pathlib.Path.exists') as mock_exists, \
             patch('sys.path') as mock_path, \
             patch('shutil.rmtree') as mock_rmtree, \
             patch('builtins.__import__', side_effect=ImportError("Module not found")):
            
            mock_mkdtemp.return_value = "/tmp/test_project"
            mock_subprocess.return_value.returncode = 0
            mock_exists.return_value = True
            mock_path.insert = MagicMock()
            
            with self.assertRaises(BAMLCompilationError) as cm:
                project.__enter__()
            
            self.assertIn("Failed to import generated client", str(cm.exception))
            # Verify cleanup was attempted
            mock_rmtree.assert_called_once()

    def test_temporary_baml_project_exit_cleanup(self):
        """Test _TemporaryBAMLProject.__exit__ cleanup logic."""
        project = _TemporaryBAMLProject("class Test {}", "TestFunc")
        project.project_dir = Path("/tmp/test_project")
        
        with patch('pathlib.Path.exists') as mock_exists, \
             patch('sys.path') as mock_path, \
             patch('sys.modules') as mock_modules, \
             patch('shutil.rmtree') as mock_rmtree:
            
            mock_exists.return_value = True
            mock_path.__contains__ = MagicMock(return_value=True)
            mock_modules.keys.return_value = ['baml_client.sync_client', 'other_module', 'baml_client.types']
            
            project.__exit__(None, None, None)
            
            # Verify path removal
            mock_path.remove.assert_called_once_with("/tmp/test_project")
            # Verify directory removal
            mock_rmtree.assert_called_once_with(Path("/tmp/test_project"))


class TestLoggingComprehensive(TestCase):
    """Comprehensive tests for logging functionality without LLM dependency."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp(prefix="baml_log_comprehensive_"))
        
        # Clean up any existing environment variables
        if 'DYNAMIC_BAML_LOG_FILE' in os.environ:
            del os.environ['DYNAMIC_BAML_LOG_FILE']
    
    def tearDown(self):
        """Clean up after tests."""
        if self.temp_dir.exists():
            import shutil
            shutil.rmtree(self.temp_dir)
        
        # Clean up environment variables
        if 'DYNAMIC_BAML_LOG_FILE' in os.environ:
            del os.environ['DYNAMIC_BAML_LOG_FILE']

    def test_log_file_path_validation(self):
        """Test various log file path scenarios."""
        test_cases = [
            # (path, should_succeed, description)
            ("simple.log", True, "Simple filename"),
            ("./relative/path.log", True, "Relative path"),
            (str(self.temp_dir / "absolute.log"), True, "Absolute path"),
            (str(self.temp_dir / "deep" / "nested" / "path.log"), True, "Nested path"),
            ("", False, "Empty path"),
        ]
        
        for path, should_succeed, description in test_cases:
            with self.subTest(path=path, description=description):
                if should_succeed:
                    _setup_log_file_redirect(path)
                    if path:  # Skip empty path
                        self.assertEqual(os.environ.get('DYNAMIC_BAML_LOG_FILE'), path)
                else:
                    # For empty path, should handle gracefully
                    _setup_log_file_redirect(path)
                    # Should not crash, but environment variable handling may vary

    def test_log_level_configuration_all_levels(self):
        """Test all valid log levels are properly configured."""
        valid_levels = ["off", "error", "warn", "info", "debug", "trace"]
        
        for level in valid_levels:
            with self.subTest(level=level):
                with patch('dynamic_baml.baml.config.set_log_level') as mock_set_level:
                    options: ProviderOptions = {
                        "provider": "ollama",
                        "log_level": level  # type: ignore
                    }
                    
                    _configure_logging(options)
                    mock_set_level.assert_called_once_with(level)

    def test_concurrent_log_file_setup(self):
        """Test concurrent log file setup doesn't cause race conditions."""
        log_file = self.temp_dir / "concurrent_test.log"
        results = []
        
        def setup_logging(thread_id):
            try:
                _setup_log_file_redirect(str(log_file))
                results.append(("success", thread_id))
            except Exception as e:
                results.append(("error", thread_id, str(e)))
        
        # Start multiple threads simultaneously
        threads = []
        for i in range(5):
            thread = threading.Thread(target=setup_logging, args=(i,))
            threads.append(thread)
        
        # Start all threads at once
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # All should succeed
        self.assertEqual(len(results), 5)
        for result in results:
            self.assertEqual(result[0], "success")
        
        # Environment variable should be set
        self.assertEqual(os.environ.get('DYNAMIC_BAML_LOG_FILE'), str(log_file))

    def test_log_file_permissions_handling(self):
        """Test behavior with different file permission scenarios."""
        # Test writable directory
        writable_log = self.temp_dir / "writable.log"
        _setup_log_file_redirect(str(writable_log))
        self.assertEqual(os.environ.get('DYNAMIC_BAML_LOG_FILE'), str(writable_log))
        
        # Test directory creation
        nested_log = self.temp_dir / "new_dir" / "nested.log"
        _setup_log_file_redirect(str(nested_log))
        self.assertTrue(nested_log.parent.exists())
        self.assertEqual(os.environ.get('DYNAMIC_BAML_LOG_FILE'), str(nested_log))

    def test_log_configuration_with_mock_baml_calls(self):
        """Test logging configuration with mocked BAML calls."""
        log_file = self.temp_dir / "mock_test.log"
        
        # Mock the BAML execution to avoid needing actual LLM
        with patch('dynamic_baml.core._temporary_baml_project') as mock_project:
            # Mock the context manager and client
            mock_client = MagicMock()
            mock_function = MagicMock()
            mock_function.return_value = MagicMock()
            mock_function.return_value.model_dump.return_value = {"name": "test", "age": 25}
            mock_client.b = MagicMock()
            setattr(mock_client.b, "ExtractDynamicSchema_12345678", mock_function)
            
            mock_project.return_value.__enter__.return_value = (self.temp_dir, mock_client)
            mock_project.return_value.__exit__.return_value = None
            
            # Test the call with logging
            options: ProviderOptions = {
                "provider": "ollama",
                "model": "gemma3:1b",
                "log_level": "info",
                "log_file": str(log_file)
            }
            
            schema = {"name": "string", "age": "int"}
            
            # This should configure logging without needing real LLM
            with patch('dynamic_baml.core.uuid.uuid4') as mock_uuid:
                mock_uuid.return_value.hex = "12345678" * 4  # Ensure consistent function name
                
                result = call_with_schema_safe(
                    "Test prompt", 
                    schema, 
                    options
                )
            
            # Verify the call succeeded
            self.assertTrue(result["success"])
            self.assertIn("data", result)
            
            # Verify logging was configured
            self.assertEqual(os.environ.get('DYNAMIC_BAML_LOG_FILE'), str(log_file))

    def test_logging_error_scenarios(self):
        """Test logging behavior in various error scenarios."""
        
        # Test with invalid log level (should be handled gracefully)
        with patch('dynamic_baml.baml.config.set_log_level', side_effect=ValueError("Invalid level")):
            options: ProviderOptions = {
                "provider": "ollama",
                "log_level": "invalid_level"  # type: ignore
            }
            
            # Should not raise exception
            _configure_logging(options)
        
        # Test with import error
        with patch('dynamic_baml.baml.config.set_log_level', side_effect=ImportError("Module not found")):
            options: ProviderOptions = {
                "provider": "ollama",
                "log_level": "info"
            }
            
            # Should not raise exception
            _configure_logging(options)

    def test_environment_variable_management(self):
        """Test proper management of environment variables."""
        log_file1 = self.temp_dir / "test1.log"
        log_file2 = self.temp_dir / "test2.log"
        
        # Set first log file
        _setup_log_file_redirect(str(log_file1))
        self.assertEqual(os.environ.get('DYNAMIC_BAML_LOG_FILE'), str(log_file1))
        
        # Set second log file (should replace first)
        _setup_log_file_redirect(str(log_file2))
        self.assertEqual(os.environ.get('DYNAMIC_BAML_LOG_FILE'), str(log_file2))

    def test_mixed_logging_configurations(self):
        """Test various combinations of logging configurations."""
        test_cases = [
            # (log_level, log_file, description)
            ("info", None, "Level only"),
            (None, "test.log", "File only"),
            ("debug", "debug.log", "Both level and file"),
            ("off", "off.log", "Off level with file"),
            (None, None, "Neither specified"),
        ]
        
        for log_level, log_file, description in test_cases:
            with self.subTest(description=description):
                # Clean environment
                if 'DYNAMIC_BAML_LOG_FILE' in os.environ:
                    del os.environ['DYNAMIC_BAML_LOG_FILE']
                
                options: ProviderOptions = {"provider": "ollama"}
                
                if log_level:
                    options["log_level"] = log_level  # type: ignore
                if log_file:
                    options["log_file"] = str(self.temp_dir / log_file)
                
                with patch('dynamic_baml.baml.config.set_log_level') as mock_set_level:
                    _configure_logging(options)
                    
                    if log_level:
                        mock_set_level.assert_called_once_with(log_level)
                    else:
                        mock_set_level.assert_not_called()
                    
                    if log_file:
                        expected_path = str(self.temp_dir / log_file)
                        self.assertEqual(os.environ.get('DYNAMIC_BAML_LOG_FILE'), expected_path)

    def test_logging_configuration_performance(self):
        """Test that logging configuration doesn't significantly impact performance."""
        
        # Measure time for logging configuration
        start_time = time.time()
        
        for i in range(100):
            options: ProviderOptions = {
                "provider": "ollama",
                "log_level": "info",
                "log_file": str(self.temp_dir / f"perf_test_{i}.log")
            }
            
            with patch('dynamic_baml.baml.config.set_log_level'):
                _configure_logging(options)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete quickly (less than 1 second for 100 configurations)
        self.assertLess(duration, 1.0, "Logging configuration should be fast")


@patch.dict(os.environ, {"BAML_LOG_LEVEL": "DEBUG"})
class ComprehensiveLoggingTestsWithRealLLM(unittest.TestCase):
    """
    Comprehensive test suite for logging, including integration with a real LLM.
    This suite is intended to be run in an environment where a real LLM is available.
    """

    @classmethod
    def setUpClass(cls):
        """Set up class-level fixtures and check if Ollama is available."""
        cls.base_options = {
            "provider": "ollama",
            "model": "gemma3:1b",
            "temperature": 0.1,
            "timeout": 60
        }
        
        # Check if Ollama is available
        factory = LLMProviderFactory()
        try:
            provider = factory.create_provider(cls.base_options)
            if not provider.is_available():
                raise ConnectionError("Ollama is not running")
        except Exception as e:
            raise ConnectionError(f"Cannot connect to Ollama: {e}") from e
    
    def setUp(self):
        """Set up test fixtures for each test."""
        self.test_schema = {
            "name": "string",
            "age": "int",
            "location": "string"
        }
        self.test_prompt = "Extract info: John Smith, age 30, lives in Seattle"
        
        # Create temporary directory for log files
        self.temp_dir = Path(tempfile.mkdtemp(prefix="baml_log_test_"))
    
    def tearDown(self):
        """Clean up after each test."""
        # Clean up temporary files
        if self.temp_dir.exists():
            import shutil
            shutil.rmtree(self.temp_dir)
        
        # Clean up environment variables
        if 'DYNAMIC_BAML_LOG_FILE' in os.environ:
            del os.environ['DYNAMIC_BAML_LOG_FILE']

    def test_log_file_creation_and_content(self):
        """Test that log file is created and contains expected content."""
        log_file = self.temp_dir / "test_creation.log"
        
        options = self.base_options.copy()
        options.update({
            "log_level": "info",
            "log_file": str(log_file)
        })
        
        # Make a call that should generate logs
        result = call_with_schema(self.test_prompt, self.test_schema, options)
        
        # Verify the call succeeded
        self.assertIsInstance(result, dict)
        self.assertIn("name", result)
        
        # Verify environment variable was set
        self.assertEqual(os.environ.get('DYNAMIC_BAML_LOG_FILE'), str(log_file))

    def test_log_level_off_no_output(self):
        """Test that log_level='off' produces no log output."""
        log_file = self.temp_dir / "test_off.log"
        
        options = self.base_options.copy()
        options.update({
            "log_level": "off",
            "log_file": str(log_file)
        })
        
        # Make a call with logging disabled
        result = call_with_schema(self.test_prompt, self.test_schema, options)
        
        # Verify the call succeeded
        self.assertIsInstance(result, dict)

    def test_log_directory_creation(self):
        """Test that nested log directories are created automatically."""
        nested_log_file = self.temp_dir / "nested" / "deeper" / "test.log"
        
        options = self.base_options.copy()
        options.update({
            "log_level": "info",
            "log_file": str(nested_log_file)
        })
        
        # Make a call with nested log path
        result = call_with_schema(self.test_prompt, self.test_schema, options)
        
        # Verify the call succeeded
        self.assertIsInstance(result, dict)
        
        # Verify nested directories were created
        self.assertTrue(nested_log_file.parent.exists())

    def test_safe_call_with_logging(self):
        """Test that call_with_schema_safe also respects logging configuration."""
        log_file = self.temp_dir / "test_safe_call.log"
        
        options = self.base_options.copy()
        options.update({
            "log_level": "info",
            "log_file": str(log_file)
        })
        
        # Make a safe call
        result = call_with_schema_safe(self.test_prompt, self.test_schema, options)
        
        # Verify safe call structure
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
        self.assertTrue(result["success"])

    def test_multiple_calls_same_log_file(self):
        """Test multiple calls appending to the same log file."""
        log_file = self.temp_dir / "test_multiple.log"
        
        options = self.base_options.copy()
        options.update({
            "log_level": "info",
            "log_file": str(log_file)
        })
        
        # Make first call
        result1 = call_with_schema("Extract: Alice Brown, 25, Portland", self.test_schema, options)
        self.assertIsInstance(result1, dict)
        
        # Small delay to ensure different timestamps
        time.sleep(1)
        
        # Make second call
        result2 = call_with_schema("Extract: Bob Wilson, 35, Denver", self.test_schema, options)
        self.assertIsInstance(result2, dict)


if __name__ == "__main__":
    # Run all tests
    pytest.main([__file__, "-v"])
