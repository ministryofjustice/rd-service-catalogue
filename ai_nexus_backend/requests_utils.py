"""Utilities common across generic requests sessions."""

from typing import List

import requests


def _configure_requests(
    n: int = 5,
    backoff_f: float = 0.1,
    force_on: List[int] = [500, 502, 503, 504],
) -> requests.Session:
    """Set up a request session with retry.

    Parameters
    ----------
    n : int, optional
        Number of retries, by default 5
    backoff_f : float, optional
        backoff_factor, by default 0.1
    force_on : List[int], optional
        HTTP status errors to retry, by default [500,502,503,504]

    Returns
    -------
    requests.Session
        The requests session configured with the specified retry strategy.

    """
    # configure scrape session
    s = requests.Session()
    retries = requests.adapters.Retry(
        total=n, backoff_factor=backoff_f, status_forcelist=force_on
    )
    s.mount("https://", requests.adapters.HTTPAdapter(max_retries=retries))
    return s


def _url_defence(url: str, exp_protocol: str = "https://") -> None:
    """Internal utility for defence checking urls."""
    if not isinstance(url, str):
        raise TypeError(f"`url` requires a string, found {type(url)}")
    elif not url.startswith(exp_protocol):
        raise ValueError(f"`url` should start with '{exp_protocol}'")
    else:
        pass
