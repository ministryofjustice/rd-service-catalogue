"""Testing integration with Confluence API."""

from mockito import when, unstub
import pytest
from requests import Session
from requests.adapters import Retry

from ai_nexus_backend.confluence_api import ConfluenceClient


class TestConfluenceClient:
    """Tests for ConfluenceClient."""

    @pytest.fixture(scope="function")
    def creds(self):
        """Returns placeholders for API authentication."""
        return {
            "MOCK_EMAIL": "foo",
            "MOCK_PAT": "bar",
            "MOCK_AGENT": "foobar",
        }

    @pytest.fixture(scope="function")
    def confluence_client(self, creds):
        """Instantiate ConfluenceClient with placeholder creds."""
        client = ConfluenceClient(
            creds["MOCK_EMAIL"],
            creds["MOCK_PAT"],
            creds["MOCK_AGENT"],
        )
        return client

    def test_confluence_client_init(self, creds, confluence_client):
        """Test properties on init"""
        client = confluence_client
        assert isinstance(client, ConfluenceClient)
        assert hasattr(client, "_ConfluenceClient__agent")
        assert hasattr(client, "_ConfluenceClient__email")
        assert hasattr(client, "_ConfluenceClient__pat")
        assert hasattr(client, "_session")
        assert client._ConfluenceClient__agent == creds["MOCK_AGENT"]
        assert client._ConfluenceClient__email == creds["MOCK_EMAIL"]
        assert client._ConfluenceClient__pat == creds["MOCK_PAT"]
        assert isinstance(client._session, Session)
        assert client._session.headers["User-Agent"] == creds["MOCK_AGENT"]
        assert client._session.headers["Accept"] == "application/json"
        assert client._session.auth == (
            creds["MOCK_EMAIL"],
            creds["MOCK_PAT"],
        )

    def test__url_defence(self, confluence_client):
        """Test defensive utility raises as expected."""
        client = confluence_client
        # test type defence
        with pytest.raises(TypeError, match=".* found <class 'int'>"):
            client._url_defence(url=1)
        with pytest.raises(TypeError, match=".* found <class 'float'>"):
            client._url_defence(url=1.0)
        with pytest.raises(TypeError, match=".* found <class 'bool'>"):
            client._url_defence(url=False)
        with pytest.raises(TypeError, match=".* found <class 'NoneType'>"):
            client._url_defence(url=None)
        # test values
        with pytest.raises(
            ValueError, match="`url` should start with 'https://'"
        ):
            client._url_defence(url="http://something")

    def test__configure_atlassian(self, confluence_client):
        """Check that default requests session can be reconfigured."""
        client = confluence_client
        new_sess = Session()
        new_sess.mount("https://", Retry(total=100))
        client._configure_atlassian(_session=new_sess)
        assert (
            client._session.adapters["https://"].total
            == new_sess.adapters["https://"].total
        )

    def test_find_code_metadata(self, confluence_client):
        """Test find_code_metadata method with mocked response."""

        def mock_response(url):
            """Return a mock response object with code block element."""

            class MockResponse:
                @property
                def content(self):
                    if url == "https://example.com/no_code_block":
                        return b"<div>No code block here</div>"
                    elif url == "https://example.com/single_code_block":
                        return b'<code>{"title": "awesome project"}</code>'
                    elif url == "https://example.com/multiple_code_blocks":
                        return (
                            b'<code>{"title": "first project"}</code>'
                            + b'<code>{"title": "second project"}</code>'
                        )

            return MockResponse()

        # set up
        client = confluence_client
        # single code block should pass -----------------------------------
        # Mock the _get_atlassian_page_content method
        url = "https://example.com/single_code_block"
        when(client)._get_atlassian_page_content(url).thenReturn(
            mock_response
        )
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
            mock_response
        )
        client.response = mock_response(url)
        with pytest.raises(
            ValueError, match="No code elements were found on this page."
        ):
            client.find_code_metadata(url)
        unstub()
        # multiple code blocks has not been implemented -------------------
        url = "https://example.com/multiple_code_blocks"
        when(client)._get_atlassian_page_content(url).thenReturn(
            mock_response
        )
        client.response = mock_response(url)
        with pytest.raises(
            NotImplementedError,
            match="More than one code block was found on this page.",
        ):
            client.find_code_metadata(url)
        unstub()

    def test_return_page_text(self, confluence_client):
        """Test return_page_text method with mocked response."""

        def mock_response(url):
            """Return a mock response object with code block element."""

            class MockResponse:
                bad_url = "https://example.com/doesnotexist"
                good_url = "https://example.com/blog"

                @property
                def text(self, url1=bad_url, url2=good_url):
                    if url == url1:
                        return None
                    elif url == url2:
                        return "<p>Some content.</p>"

                @property
                def status_code(self, url1=bad_url, url2=good_url):
                    if url == url1:
                        return 404
                    elif url == url2:
                        return 200

                @property
                def ok(self, url1=bad_url, url2=good_url):
                    if url == url1:
                        return False
                    elif url == url2:
                        return True

                def raise_for_status(self):
                    """Simulate raising an HTTPError for bad responses."""
                    if self.status_code != 200:
                        raise ValueError(f"HTTP Error: {self.status_code}")

            return MockResponse()

        # set up
        client = confluence_client

        # Case where url exists, stub values ------------------------------
        url = "https://example.com/blog"
        when(client._session).get(url).thenReturn(mock_response(url))
        client.response = mock_response(url)
        assert client.return_page_text(url) == "<p>Some content.</p>"
        unstub()
        # case where url doesn't exist ------------------------------------
        url = "https://example.com/doesnotexist"
        when(client._session).get(url).thenReturn(mock_response(url))
        with pytest.raises(ValueError, match="HTTP Error: 404"):
            client.return_page_text(url)
