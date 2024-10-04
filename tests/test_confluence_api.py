"""Testing integration with Confluence API."""
import pytest
from requests import Session

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
        assert hasattr(client, "_session")
        assert client._ConfluenceClient__agent == mock_creds["MOCK_AGENT"]
        assert client._ConfluenceClient__email == mock_creds["MOCK_EMAIL"]
        assert client._ConfluenceClient__pat == mock_creds["MOCK_PAT"]
        assert isinstance(client._session, Session)
        assert client._session.headers["User-Agent"] == mock_creds[
            "MOCK_AGENT"
            ]
        assert client._session.headers["Accept"] == "application/json"
        assert client._session.auth == (
            mock_creds["MOCK_EMAIL"], mock_creds["MOCK_PAT"]
            )
