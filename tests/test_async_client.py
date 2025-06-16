import unittest
from unittest.mock import MagicMock, patch
import baml_py
import importlib

# This is a generated file, so we have to do some weird imports.
import dynamic_baml.baml.async_client as async_client_module

class TestAsyncClient(unittest.TestCase):
    @patch('dynamic_baml.baml.globals.DO_NOT_USE_DIRECTLY_UNLESS_YOU_KNOW_WHAT_YOURE_DOING_RUNTIME')
    @patch('baml_py.BamlStream')
    def test_baml_stream_client_extract_resume(self, mock_baml_stream, mock_runtime):
        """Test BamlStreamClient.ExtractResume method."""
        # Mock the __getitem__ method to handle generic type usage.
        mock_baml_stream.__getitem__.return_value = MagicMock()

        # Reload the module to pick up the mocks.
        importlib.reload(async_client_module)
        stream_client = async_client_module.b.stream

        mock_ffi_stream = MagicMock()
        mock_ffi_stream.on_event.return_value = mock_ffi_stream
        mock_runtime.stream_function.return_value = mock_ffi_stream

        resume_text = "This is a resume"
        result = stream_client.ExtractResume(resume=resume_text)

        mock_runtime.stream_function.assert_called_once()
        args, kwargs = mock_runtime.stream_function.call_args
        self.assertEqual(args[0], "ExtractResume")
        self.assertEqual(args[1], {"resume": resume_text})
        
        mock_baml_stream.__getitem__.assert_called()
        self.assertIsInstance(result, MagicMock) 