"""Testing integration with Confluence API."""
import pytest

from ai_nexus.confluence_api import ConfluenceClient


class TestConfluenceClient:
    """Tests for ConfluenceClient."""
    @pytest.fixture(scope="class")
    def mock_creds(self):
        """Returns placeholders for API authentication."""
        return {
            "MOCK_EMAIL" : "foo",
            "MOCK_PAT" : "bar",
            "MOCK_AGENT" : "foobar",
            }


    def test_confluence_client_init(self, mock_creds):
        """Test properties on init"""
        client = ConfluenceClient(
            atlassian_email=mock_creds["MOCK_EMAIL"],
            atlassian_pat=mock_creds["MOCK_PAT"],
            user_agent=mock_creds["MOCK_AGENT"],
            )
        assert isinstance(client, ConfluenceClient)
        assert hasattr(client, "_ConfluenceClient__agent")
        assert hasattr(client, "_ConfluenceClient__email")
        assert hasattr(client, "_ConfluenceClient__pat")
