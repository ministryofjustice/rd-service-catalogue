"""Testing integration with Confluence API."""
from mockito import when, unstub
import pytest
from requests import Session
from requests.adapters import HTTPAdapter, Retry

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
    

    def test__url_defence(self, mock_creds):
        """Test defensive utility raises as expected."""
        client = ConfluenceClient(
            mock_creds["MOCK_EMAIL"],
            mock_creds["MOCK_PAT"],
            mock_creds["MOCK_AGENT"],
            )
        with pytest.raises(TypeError, match=".* found <class 'int'>"):
            client._url_defence(url=1)
        with pytest.raises(TypeError, match=".* found <class 'float'>"):
            client._url_defence(url=1.0)
        with pytest.raises(TypeError, match=".* found <class 'bool'>"):
            client._url_defence(url=False)
        with pytest.raises(TypeError, match=".* found <class 'NoneType'>"):
            client._url_defence(url=None)
    

    def test__configure_atlassian(self, mock_creds):
        """Check that default requests session can be reconfigured."""
        client = ConfluenceClient(
            mock_creds["MOCK_EMAIL"],
            mock_creds["MOCK_PAT"],
            mock_creds["MOCK_AGENT"],
        )
        new_sess = Session()
        new_sess.mount("https://", Retry(total=100))
        client._configure_atlassian(_session=new_sess)
        assert client._session.adapters[
            "https://"
            ].total == new_sess.adapters["https://"].total
    

    def test_find_code_metadata(self, mock_creds):
        """Test find_code_metadata method with mocked response."""


        def mock_response(url):
            """Return a mock response object with code block element."""
            class MockResponse:
                @property
                def content(self):
                    if url == "https://example.com/no_code_block":
                        return b'<div>No code block here</div>'
                    elif url == "https://example.com/single_code_block":
                        return b'<code>{"title": "awesome project"}</code>'
                    elif url == "https://example.com/multiple_code_blocks":
                        return (
                            b'<code>{"title": "first project"}</code>' +
                            b'<code>{"title": "second project"}</code>'
                            )
            return MockResponse()


        # set up
        client = ConfluenceClient(
            atlassian_email=mock_creds["MOCK_EMAIL"],
            atlassian_pat=mock_creds["MOCK_PAT"],
            user_agent=mock_creds["MOCK_AGENT"],
        )
        # single code block should pass -----------------------------------
        # Mock the _get_atlassian_page_content method
        url = "https://example.com/single_code_block" 
        when(client)._get_atlassian_page_content(url).thenReturn(
            mock_response)        
        client.response = mock_response(url)
        # Use and assert
        metadata = client.find_code_metadata(url)
        # Assert the expected metadata
        assert isinstance(metadata, dict)
        expected_metadata = {"title": "awesome project"}
        assert metadata == expected_metadata
        unstub()
        # no code block must raise ----------------------------------------
        url = "https://example.com/no_code_block"
        when(client)._get_atlassian_page_content(url).thenReturn(
            mock_response)
        client.response = mock_response(url)
        with pytest.raises(
            ValueError, match="No code elements were found on this page."
            ):
            client.find_code_metadata(url)
        unstub()
        # multiple code blocks has not been implemented -------------------
        url = "https://example.com/multiple_code_blocks"
        when(client)._get_atlassian_page_content(url).thenReturn(
            mock_response)
        client.response = mock_response(url)
        with pytest.raises(
            NotImplementedError,
            match="More than one code block was found on this page."):
            client.find_code_metadata(url)
        unstub()
