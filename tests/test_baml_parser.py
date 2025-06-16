"""
Tests for the BAML parsers.
"""

import unittest
from unittest.mock import MagicMock

from dynamic_baml.baml import parser, types, partial_types

class TestBamlParser(unittest.TestCase):

    def setUp(self):
        self.runtime_mock = MagicMock()
        self.ctx_manager_mock = MagicMock()
        self.response_parser = parser.LlmResponseParser(self.runtime_mock, self.ctx_manager_mock)
        self.stream_parser = parser.LlmStreamParser(self.runtime_mock, self.ctx_manager_mock)

    def test_llm_response_parser_extract_resume(self):
        """Test LlmResponseParser.ExtractResume method."""
        llm_response = '{"name": "John Doe", "email": "j.doe@example.com"}'
        expected_resume = types.Resume(name="John Doe", email="j.doe@example.com", experience=[], skills=[])
        
        self.runtime_mock.parse_llm_response.return_value = expected_resume

        result = self.response_parser.ExtractResume(llm_response)

        self.runtime_mock.parse_llm_response.assert_called_once_with(
            "ExtractResume",
            llm_response,
            types,
            types,
            partial_types,
            False,
            self.ctx_manager_mock.get(),
            None,
            None,
        )
        self.assertEqual(result, expected_resume)

    def test_llm_stream_parser_extract_resume(self):
        """Test LlmStreamParser.ExtractResume method."""
        llm_response = '{"name": "Jane Doe"}'
        # Note: We are not creating a partial_types.Resume object here because the fields are not optional.
        # Instead, we are just mocking the return value from the runtime.
        expected_partial_resume = MagicMock()
        
        self.runtime_mock.parse_llm_response.return_value = expected_partial_resume

        result = self.stream_parser.ExtractResume(llm_response)

        self.runtime_mock.parse_llm_response.assert_called_once_with(
            "ExtractResume",
            llm_response,
            types,
            types,
            partial_types,
            True,
            self.ctx_manager_mock.get(),
            None,
            None,
        )
        self.assertEqual(result, expected_partial_resume)

    def test_llm_response_parser_with_baml_options(self):
        """Test LlmResponseParser.ExtractResume with baml_options."""
        llm_response = '{"name": "John Doe"}'
        tb_mock = MagicMock()
        tb_mock._tb = "internal_tb_mock"
        cr_mock = MagicMock()
        baml_options = {"tb": tb_mock, "client_registry": cr_mock}
        
        self.response_parser.ExtractResume(llm_response, baml_options=baml_options)

        self.runtime_mock.parse_llm_response.assert_called_with(
            "ExtractResume",
            llm_response,
            types,
            types,
            partial_types,
            False,
            self.ctx_manager_mock.get(),
            "internal_tb_mock",
            cr_mock,
        )

    def test_llm_stream_parser_with_baml_options(self):
        """Test LlmStreamParser.ExtractResume with baml_options."""
        llm_response = '{"name": "Jane Doe"}'
        tb_mock = MagicMock()
        tb_mock._tb = "internal_tb_mock"
        cr_mock = MagicMock()
        baml_options = {"tb": tb_mock, "client_registry": cr_mock}

        self.stream_parser.ExtractResume(llm_response, baml_options=baml_options)

        self.runtime_mock.parse_llm_response.assert_called_with(
            "ExtractResume",
            llm_response,
            types,
            types,
            partial_types,
            True,
            self.ctx_manager_mock.get(),
            "internal_tb_mock",
            cr_mock,
        )


if __name__ == "__main__":
    unittest.main() 