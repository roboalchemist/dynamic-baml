"""
Tests for the BAML asynchronous request builders.
"""

import unittest
from unittest.mock import MagicMock, AsyncMock

from dynamic_baml.baml import async_request

class TestBamlAsyncRequest(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.runtime_mock = MagicMock()
        self.runtime_mock.build_request = AsyncMock()
        self.ctx_manager_mock = MagicMock()
        self.http_request = async_request.AsyncHttpRequest(self.runtime_mock, self.ctx_manager_mock)
        self.http_stream_request = async_request.AsyncHttpStreamRequest(self.runtime_mock, self.ctx_manager_mock)

    async def test_http_request_extract_resume(self):
        """Test AsyncHttpRequest.ExtractResume method."""
        resume_text = "This is a resume."
        await self.http_request.ExtractResume(resume_text)

        self.runtime_mock.build_request.assert_called_once_with(
            "ExtractResume",
            {"resume": resume_text},
            self.ctx_manager_mock.get(),
            None,
            None,
            False,
        )

    async def test_http_stream_request_extract_resume(self):
        """Test AsyncHttpStreamRequest.ExtractResume method."""
        resume_text = "This is a resume."
        await self.http_stream_request.ExtractResume(resume_text)

        self.runtime_mock.build_request.assert_called_once_with(
            "ExtractResume",
            {"resume": resume_text},
            self.ctx_manager_mock.get(),
            None,
            None,
            True,
        )

    async def test_http_request_with_baml_options(self):
        """Test AsyncHttpRequest.ExtractResume with baml_options."""
        resume_text = "This is a resume."
        tb_mock = MagicMock()
        tb_mock._tb = "internal_tb_mock"
        cr_mock = MagicMock()
        baml_options = {"tb": tb_mock, "client_registry": cr_mock}
        
        await self.http_request.ExtractResume(resume_text, baml_options=baml_options)

        self.runtime_mock.build_request.assert_called_with(
            "ExtractResume",
            {"resume": resume_text},
            self.ctx_manager_mock.get(),
            "internal_tb_mock",
            cr_mock,
            False,
        )

    async def test_http_stream_request_with_baml_options(self):
        """Test AsyncHttpStreamRequest.ExtractResume with baml_options."""
        resume_text = "This is a resume."
        tb_mock = MagicMock()
        tb_mock._tb = "internal_tb_mock"
        cr_mock = MagicMock()
        baml_options = {"tb": tb_mock, "client_registry": cr_mock}
        
        await self.http_stream_request.ExtractResume(resume_text, baml_options=baml_options)

        self.runtime_mock.build_request.assert_called_with(
            "ExtractResume",
            {"resume": resume_text},
            self.ctx_manager_mock.get(),
            "internal_tb_mock",
            cr_mock,
            True,
        )


if __name__ == "__main__":
    unittest.main() 