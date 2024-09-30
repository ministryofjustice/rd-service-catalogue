"""Testing integration with github API."""
import re

from mockito import when, unstub
import requests
import pytest

from ai_nexus import github_api

class TestGetReadmeContent(object):
    """Tests for get_readme_content()."""


    def test_get_readme_content_defence(self):
        """Check defensive logic."""
        with pytest.raises(
            TypeError,
            match="repo_url expected type str. Found <class 'int'>."):
            github_api.get_readme_content(
                repo_url=1, pat="foo", agent="bar"
                )
        with pytest.raises(
            ValueError,
            match=re.escape(
                "accept expects either application/vnd.github+json or app")
            ):
            github_api.get_readme_content(
                repo_url="foobar", pat="foo", agent="bar", accept="wrong",
                       )
        with pytest.raises(
            ValueError,
            match="repo_url should begin with 'https://', found http://"
            ):
            github_api.get_readme_content(
                repo_url="http://NOT_SUPPORTED", pat="foo", agent="bar",
            )


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
        # repeat for accept HTML
        when(requests).get(...).thenReturn(mock_response)
        result = github_api.get_readme_content(
            "https://github.com/owner/repo",
            "fake_pat",
            "fake_agent",
            accept="application/vnd.github.html+json"
        )
        unstub()
