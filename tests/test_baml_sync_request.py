"""
Tests for the BAML synchronous request builders.
"""

import unittest
from unittest.mock import MagicMock

from dynamic_baml.baml import sync_request

class TestBamlSyncRequest(unittest.TestCase):

    def setUp(self):
        self.runtime_mock = MagicMock()
        self.ctx_manager_mock = MagicMock()
        self.http_request = sync_request.HttpRequest(self.runtime_mock, self.ctx_manager_mock)
        self.http_stream_request = sync_request.HttpStreamRequest(self.runtime_mock, self.ctx_manager_mock)

    def test_http_request_extract_resume(self):
        """Test HttpRequest.ExtractResume method."""
        resume_text = "This is a resume."
        self.http_request.ExtractResume(resume_text)

        self.runtime_mock.build_request_sync.assert_called_once_with(
            "ExtractResume",
            {"resume": resume_text},
            self.ctx_manager_mock.get(),
            None,
            None,
            False,
        )

    def test_http_stream_request_extract_resume(self):
        """Test HttpStreamRequest.ExtractResume method."""
        resume_text = "This is a resume."
        self.http_stream_request.ExtractResume(resume_text)

        self.runtime_mock.build_request_sync.assert_called_once_with(
            "ExtractResume",
            {"resume": resume_text},
            self.ctx_manager_mock.get(),
            None,
            None,
            True,
        )

    def test_http_request_with_baml_options(self):
        """Test HttpRequest.ExtractResume with baml_options."""
        resume_text = "This is a resume."
        tb_mock = MagicMock()
        tb_mock._tb = "internal_tb_mock"
        cr_mock = MagicMock()
        baml_options = {"tb": tb_mock, "client_registry": cr_mock}
        
        self.http_request.ExtractResume(resume_text, baml_options=baml_options)

        self.runtime_mock.build_request_sync.assert_called_with(
            "ExtractResume",
            {"resume": resume_text},
            self.ctx_manager_mock.get(),
            "internal_tb_mock",
            cr_mock,
            False,
        )

    def test_http_stream_request_with_baml_options(self):
        """Test HttpStreamRequest.ExtractResume with baml_options."""
        resume_text = "This is a resume."
        tb_mock = MagicMock()
        tb_mock._tb = "internal_tb_mock"
        cr_mock = MagicMock()
        baml_options = {"tb": tb_mock, "client_registry": cr_mock}
        
        self.http_stream_request.ExtractResume(resume_text, baml_options=baml_options)

        self.runtime_mock.build_request_sync.assert_called_with(
            "ExtractResume",
            {"resume": resume_text},
            self.ctx_manager_mock.get(),
            "internal_tb_mock",
            cr_mock,
            True,
        )


if __name__ == "__main__":
    unittest.main() 