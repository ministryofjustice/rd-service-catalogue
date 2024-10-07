"""Integrating with Atlassian confluence api."""

import json

from bs4 import BeautifulSoup
from requests import HTTPError, Response

from ai_nexus_backend.request_utils import _configure_requests


class ConfluenceClient:
    """A client for interacting with the Atlassian Confluence API.

    This class provides methods to retrieve and parse content from
    Confluence pages.

    Parameters
    ----------
    atlassian_email : str, optional
        The email address associated with the Atlassian account.
    atlassian_pat : str, optional
        The personal access token for authentication.
    user_agent : str, optional
        The user agent string to be used in HTTP requests.

    Attributes
    ----------
    soup : BeautifulSoup, optional
        The parsed HTML content of the last retrieved Confluence page.
    metadata : dict, optional
        The metadata extracted from the code block in the last retrieved
        page.

    Methods
    -------
    find_code_metadata(url:str) -> dict
        Extracts metadata from present in a code block for the provided
        url.
    return_page_text(url:str) -> str
        Returns the web page text for the provided url.
    """

    def __init__(self, atlassian_email, atlassian_pat, user_agent=None):
        self.__email = atlassian_email
        self.__pat = atlassian_pat
        self.__agent = user_agent
        self._session = self._configure_atlassian()

    def _url_defence(self, url: str) -> None:
        """Internal utility for defence checking urls."""
        if not isinstance(url, str):
            raise TypeError(f"`url` requires a string, found {type(url)}")
        elif not url.startswith(r"https://"):
            raise ValueError("`url` should start with 'https://'")
        else:
            pass

    def _configure_atlassian(self, _session=_configure_requests()):
        """Set up a request Session with retry & backoff spec."""
        _session.auth = (self.__email, self.__pat)
        if self.__agent:
            # 'python-requests/version by default'
            _session.headers["User-Agent"] = self.__agent
        _session.headers["Accept"] = "application/json"
        _session.headers["Content-Type"] = "application/json"
        self._session = _session
        return _session

    def _get_atlassian_page_content(self, url: str) -> Response:
        """Get the content of a specified Confluence page.

        Updates the `response` attribute.

        Parameters
        ----------
        url : str
            The URL of the Confluence page.

        Returns
        -------
        The response from the Confluence API, also updates the instance's
        state.

        Raises
        ------
        TypeError
            If `url` is not a string.
        HTTPError
            If the HTTP request to the Confluence API fails.
        """
        if not isinstance(url, str):
            raise TypeError()
        resp = self._session.get(url)
        if resp.ok:
            self.response = resp
            return resp
        else:
            raise HTTPError(resp.raise_for_status())

    def find_code_metadata(self, url: str) -> dict:
        """
        Extracts metadata from a code block in page content.

        Currently only works for pages with a single, dedicated code
        element.

        Parameters
        ----------
        url : str
            The URL of the Confluence page.

        Returns
        -------
        dict
            A dictionary containing the extracted metadata.

        Raises
        ------
        TypeError
            If `soup` is not a BeautifulSoup object or None.
        ValueError
            If no code elements are found.
        NotImplementedError
            If more than one code block is found on the page.
        """
        self._url_defence(url)
        self._get_atlassian_page_content(url)  # updates self.response
        soup = BeautifulSoup(self.response.content, "html.parser")
        # there must be a single code element, cannot set or target an ID
        code_elements = soup.find_all("code")
        n = len(code_elements)
        if n == 0:
            raise ValueError("No code elements were found on this page.")
        elif n > 1:
            raise NotImplementedError(
                "More than one code block was found on this page."
            )
        meta = json.loads(code_elements[0].text)
        self.metadata = meta
        return meta

    def return_page_text(self, url: str) -> str:
        """Returns text from confluence page content.

        Parameters
        ----------
        url : str
            The URL of the Confluence page.

        Returns
        -------
        str
            HTML text content.
        """
        self._url_defence(url)
        self._get_atlassian_page_content(url)  # updates self.response
        return self.response.text
