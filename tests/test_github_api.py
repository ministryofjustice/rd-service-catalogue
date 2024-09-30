"""Testing integration with github API."""
from mockito import when, unstub
import requests

from ai_nexus import github_api

class TestGetReadmeContent(object):
    """Tests for get_readme_content()."""


    def test_get_readme_content(self):
        """Mocked test ensuring byte code returned as expected string."""
        # Mock the response of the get_readme_content function
        mock_response = requests.Response()
        mock_response.status_code = 200
        _b1 =  b'{"content": "VGhpcyBpcyB0aGUgUkVBRE1FIGNvbnRlbnQ=",'
        _b2 = b' "encoding": "base64"}'
        _bytes = _b1 + _b2
        mock_response._content = _bytes
        # Mock the requests.get call inside get_readme_content. Needs to
        # match requests.get usage in the module.
        when(requests).get(...).thenReturn(mock_response)
        # Call & assert
        result = github_api.get_readme_content(
            "https://github.com/owner/repo", "fake_pat", "fake_agent")
        assert result == "This is the README content"
        unstub()
