"""
Tests for the BAML synchronous client.
"""

import unittest
from unittest.mock import MagicMock, patch
import baml_py

from dynamic_baml.baml import sync_client, types, partial_types

class TestBamlSyncClient(unittest.TestCase):

    def setUp(self):
        self.runtime_mock = MagicMock()
        self.ctx_manager_mock = MagicMock()
        self.client = sync_client.BamlSyncClient(self.runtime_mock, self.ctx_manager_mock)

    def test_with_options(self):
        """Test the with_options method."""
        tb_mock = MagicMock()
        cr_mock = MagicMock()
        collector_mock = MagicMock()

        new_client = self.client.with_options(tb=tb_mock, client_registry=cr_mock, collector=collector_mock)
        
        self.assertIsNot(new_client, self.client)
        self.assertIsInstance(new_client, sync_client.BamlSyncClient)
        
        # To verify the options are set, we need to inspect the internal state.
        # This is not ideal, but necessary for this test.
        self.assertEqual(new_client._BamlSyncClient__baml_options['tb'], tb_mock)
        self.assertEqual(new_client._BamlSyncClient__baml_options['client_registry'], cr_mock)
        self.assertEqual(new_client._BamlSyncClient__baml_options['collector'], collector_mock)

    def test_extract_resume(self):
        """Test the ExtractResume method."""
        resume_text = "This is a resume."
        raw_result_mock = MagicMock()
        expected_resume = types.Resume(name="test", email="test@test.com", experience=[], skills=[])
        raw_result_mock.cast_to.return_value = expected_resume

        self.runtime_mock.call_function_sync.return_value = raw_result_mock
        
        result = self.client.ExtractResume(resume_text)

        self.runtime_mock.call_function_sync.assert_called_once_with(
            "ExtractResume",
            {"resume": resume_text},
            self.ctx_manager_mock.get(),
            None,
            None,
            [],
        )
        raw_result_mock.cast_to.assert_called_once_with(types, types, partial_types, False)
        self.assertEqual(result, expected_resume)

    def test_extract_resume_with_collector(self):
        """Test ExtractResume with a single collector."""
        resume_text = "This is a resume."
        collector_mock = MagicMock()
        baml_options = {"collector": collector_mock}
        raw_result_mock = MagicMock()
        self.runtime_mock.call_function_sync.return_value = raw_result_mock
        
        self.client.ExtractResume(resume_text, baml_options=baml_options)

        self.runtime_mock.call_function_sync.assert_called_with(
            "ExtractResume",
            {"resume": resume_text},
            self.ctx_manager_mock.get(),
            None,
            None,
            [collector_mock],
        )

    def test_extract_resume_with_collector_list(self):
        """Test ExtractResume with a list of collectors."""
        resume_text = "This is a resume."
        collector_mock1 = MagicMock()
        collector_mock2 = MagicMock()
        baml_options = {"collector": [collector_mock1, collector_mock2]}
        raw_result_mock = MagicMock()
        self.runtime_mock.call_function_sync.return_value = raw_result_mock
        
        self.client.ExtractResume(resume_text, baml_options=baml_options)

        self.runtime_mock.call_function_sync.assert_called_with(
            "ExtractResume",
            {"resume": resume_text},
            self.ctx_manager_mock.get(),
            None,
            None,
            [collector_mock1, collector_mock2],
        )

    def test_properties(self):
        """Test the stream, request, parse, and parse_stream properties."""
        self.assertIsInstance(self.client.stream, sync_client.BamlStreamClient)
        self.assertIsInstance(self.client.request, sync_client.HttpRequest)
        self.assertIsInstance(self.client.parse, sync_client.LlmResponseParser)
        self.assertIsInstance(self.client.parse_stream, sync_client.LlmStreamParser)


class TestBamlStreamClient(unittest.TestCase):

    def setUp(self):
        self.runtime_mock = MagicMock()
        self.ctx_manager_mock = MagicMock()
        self.stream_client = sync_client.BamlStreamClient(self.runtime_mock, self.ctx_manager_mock)

    @patch('baml_py.stream.BamlSyncStream.__init__', return_value=None)
    def test_extract_resume_stream(self, baml_stream_mock):
        """Test the ExtractResume method of the stream client."""
        resume_text = "This is a resume stream."
        
        self.stream_client.ExtractResume(resume_text)

        self.runtime_mock.stream_function_sync.assert_called_once()
        baml_stream_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main() 