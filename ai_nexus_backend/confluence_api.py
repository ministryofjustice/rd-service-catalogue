"""Integrating with Atlassian confluence api."""

import json

from bs4 import BeautifulSoup
from requests import HTTPError, Response

from ai_nexus_backend.build_yaml import _parse_yaml
from ai_nexus_backend.requests_utils import (
    _configure_requests,
    _url_defence,
)


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
    extract_json_metadata(url:str) -> dict
        Extract metadata from a site with a JSON code block.
    extract_yaml_metadata(url:str) -> dict
        Extracts metadata from a site with a YAML code block.
    return_page_text(url:str) -> str
        Returns the web page text for the provided url.
    """

    def __init__(self, atlassian_email, atlassian_pat, user_agent=None):
        self.__email = atlassian_email
        self.__pat = atlassian_pat
        self.__agent = user_agent
        self._session = self._configure_atlassian()

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
        resp = self._session.get(url)
        if resp.ok:
            self.response = resp
            return resp
        else:
            raise HTTPError(resp.raise_for_status())

    def _find_code_metadata(self, url: str) -> dict:
        """Update meta_text attribute with content str from url."""

        _url_defence(url, param_nm="url")
        self._get_atlassian_page_content(url)  # updates self.response
        soup = BeautifulSoup(self.response.content, "html.parser")
        # there must be a single code element, cannot set or target an ID
        # in Confluence apparently, reference:
        # https://community.atlassian.com/t5/Confluence-questions/Is-it-possible-to-create-ID-s-for-web-elements/qaq-p/1891040
        code_elements = soup.find_all("code")
        n = len(code_elements)
        if n == 0:
            raise ValueError("No code elements were found on this page.")
        elif n > 1:
            raise NotImplementedError(
                "More than one code block was found on this page."
            )
        meta_text = code_elements[0].text
        self.meta_text = meta_text
        return meta_text

    def extract_json_metadata(self, url: str) -> dict:
        """
        Extracts metadata from a JSON code block in url site content.

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
        self._find_code_metadata(url)
        meta = json.loads(self.meta_text)
        self.metadata = meta
        return meta

    def extract_yaml_metadata(self, url: str) -> dict:
        """
        Extracts metadata from a YAML code block in url site content.

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
        self._find_code_metadata(url)
        meta = _parse_yaml(self.meta_text)
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
        _url_defence(url, param_nm="url")
        self._get_atlassian_page_content(url)  # updates self.response
        return self.response.text
