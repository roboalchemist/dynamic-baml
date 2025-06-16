"""
Tests for the BAML globals.
"""

import unittest
from unittest.mock import MagicMock, patch
import os

from dynamic_baml.baml import globals
from baml_py.baml_py import BamlError

class TestBamlGlobals(unittest.TestCase):

    @patch('dynamic_baml.baml.globals.DO_NOT_USE_DIRECTLY_UNLESS_YOU_KNOW_WHAT_YOURE_DOING_CTX')
    @patch('dynamic_baml.baml.globals.DO_NOT_USE_DIRECTLY_UNLESS_YOU_KNOW_WHAT_YOURE_DOING_RUNTIME')
    @patch('dynamic_baml.baml.globals.get_baml_files')
    def test_reset_baml_env_vars_success(self, get_baml_files_mock, runtime_mock, ctx_manager_mock):
        """Test the successful reset of BAML environment variables."""
        ctx_manager_mock.allow_reset.return_value = True
        env_vars = {"BAML_API_KEY": "test_key"}
        
        globals.reset_baml_env_vars(env_vars)

        runtime_mock.reset.assert_called_once_with(
            "baml_src",
            get_baml_files_mock(),
            env_vars,
        )
        ctx_manager_mock.reset.assert_called_once()

    @patch('dynamic_baml.baml.globals.DO_NOT_USE_DIRECTLY_UNLESS_YOU_KNOW_WHAT_YOURE_DOING_CTX')
    def test_reset_baml_env_vars_failure(self, ctx_manager_mock):
        """Test that reset_baml_env_vars raises a BamlError when not allowed."""
        ctx_manager_mock.allow_reset.return_value = False
        
        with self.assertRaises(BamlError):
            globals.reset_baml_env_vars({})

    def test_patched_load_dotenv_success(self):
        """Test that the patched load_dotenv calls reset_baml_env_vars."""
        with patch('dynamic_baml.baml.globals.original_load_dotenv') as original_load_dotenv_mock:
            with patch('dynamic_baml.baml.globals.reset_baml_env_vars') as reset_baml_env_vars_mock:
                globals.patched_load_dotenv()
                reset_baml_env_vars_mock.assert_called_once_with(os.environ.copy())
                original_load_dotenv_mock.assert_called_once()

    def test_patched_load_dotenv_swallows_error(self):
        """Test that the patched load_dotenv swallows BamlError."""
        with patch('dynamic_baml.baml.globals.original_load_dotenv') as original_load_dotenv_mock:
            with patch('dynamic_baml.baml.globals.reset_baml_env_vars', side_effect=BamlError) as reset_baml_env_vars_mock:
                globals.patched_load_dotenv()
                reset_baml_env_vars_mock.assert_called_once_with(os.environ.copy())
                original_load_dotenv_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main() 