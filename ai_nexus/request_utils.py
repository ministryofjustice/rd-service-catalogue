"""Utilities common across generic requests sessions."""
import requests

def _configure_requests(
    n=5, backoff_f=0.1, force_on=[500, 502, 503, 504]
) -> requests.Session:
    """Set up a request session with retry.

    Parameters
    ----------
    n : int, optional
        Number of retries, by default 5
    backoff_f : float, optional
        backoff_factor, by default 0.1
    force_on : list, optional
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
