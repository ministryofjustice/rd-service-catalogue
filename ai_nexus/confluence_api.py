"""Integrating with Atlassian confluence api."""
import json
from typing import Union

from bs4 import BeautifulSoup
from requests import HTTPError

from ai_nexus.github_api import _configure_requests


class ConfluenceClient():
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
    get_atlassian_page_content(url: str) -> BeautifulSoup
        Retrieves and parses the content of a specified Confluence page.

    find_code_metadata(soup: Union[BeautifulSoup, None] = None) -> dict
        Extracts metadata from the code block in the provided or previously
        retrieved page content.
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


    def get_atlassian_page_content(self, url:str) -> BeautifulSoup:
        """Get the content of a specified Confluence page.

        Parameters
        ----------
        url : str
            The URL of the Confluence page.

        Returns
        -------
        BeautifulSoup
            A BeautifulSoup object containing the parsed HTML content of
            the page.

        Raises
        ------
        TypeError
            If `url` is not a string.
        HTTPError
            If the HTTP request to the Confluence API fails.
        """
        if not isinstance(url, str):
            raise TypeError(f"`url` requires a string, found {type(url)}")

        resp = self._session.get(url)
        if resp.ok:
            _soup = BeautifulSoup(resp.content, "html.parser")
            self.soup = _soup
            return _soup
        else:
            raise HTTPError(resp.raise_for_status())
        

    def find_code_metadata(
            self, soup:Union[BeautifulSoup, None]=None) -> dict:
        """
        Extracts metadata from a code block in page content.

        Currently only works for pages with a single, dedicated code
        element.

        Parameters
        ----------
        soup : Union[BeautifulSoup, None], optional
            A BeautifulSoup object containing the parsed HTML content. If
            None, the method will use the last retrieved page content
            stored in the instance.

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
        if not isinstance(soup, (BeautifulSoup, type(None))):
            raise TypeError(
                f"`soup` expects BeautifulSoup or None: {type(soup)}")
        if soup:
            # user has soup without `get_moj_atlassian_page_content()`
            s = soup
        # If none, use self.soup if it exists
        elif hasattr(self, "soup"):
            s = self.soup
        else:
            raise ValueError(
                "Method requires BeautifulSoup."
                " Execute get_atlassian_page_content() first."
            )

        # there must be a single code element, cannot set or target an ID
        code_elements = s.find_all("code")
        if n := len(code_elements) == 0:
            raise ValueError("No code elements were found on this page.")
        elif n > 1:
            raise NotImplementedError(
                "More than one code block was found on this page.") 
        meta = json.loads(code_elements[0].text)
        self.metadata = meta
        return meta
