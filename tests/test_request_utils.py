"""Tests for request_utils module."""

import pytest
from requests import HTTPError, Response

from ai_nexus_backend.requests_utils import _handle_response, _url_defence


class Test_UrlDefence:

    def test__url_defence(self):
        """Test defensive utility raises as expected."""
        # test type defence
        with pytest.raises(TypeError, match=".* Found <class 'int'>"):
            _url_defence(url=1, param_nm="int")
        with pytest.raises(TypeError, match=".* Found <class 'float'>"):
            _url_defence(url=1.0, param_nm="float")
        with pytest.raises(TypeError, match=".* Found <class 'bool'>"):
            _url_defence(url=False, param_nm="bool")
        with pytest.raises(TypeError, match=".* Found <class 'NoneType'>"):
            _url_defence(url=None, param_nm="Nonetype")

        # test values
        with pytest.raises(
            ValueError,
            match="url should begin with 'https://', found http://",
        ):
            _url_defence(url="http://something", param_nm="url")

    @pytest.mark.parametrize(
        "code, msg",
        [
            (400, "Bad Request"),
            (401, "Unauthorized"),
            (403, "Forbidden"),
            (404, "Not Found"),
            (405, "Method Not Allowed"),
            (500, "Internal Server Error"),
            (502, "Bad Gateway"),
            (503, "Service Unavailable"),
            (504, "Gateway Timeout"),
        ],
    )
    def test_handle_response_errors(self, code, msg):
        """Test that an exception is raised for various error responses."""
        # simulate bad responses
        error_response = Response()
        error_response.status_code = code
        error_response.reason = msg

        with pytest.raises(HTTPError, match=f"HTTP error {code}:\n{msg}"):
            _handle_response(error_response)

    def test__handle_response_success(self):
        """Test that a successful response is returned as is."""
        # Simulate a successful response
        success_response = Response()
        success_response.status_code = 200
        success_response._content = b'{"key": "value"}'

        result = _handle_response(success_response)
        assert result == success_response
