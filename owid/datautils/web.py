"""Web utils."""

import re
import warnings
from urllib.parse import urlparse


def get_base_url(url: str, include_scheme=True) -> str:
    """Get base URL from an arbitrary URL path (e.g. "https://example.com/some/path" -> "https://example.com").

    If the given URL does not start with "http(s)://"

    Parameters
    ----------
    url : str
        Input URL.
    include_scheme : bool, optional
        True to include "http(s)://" at the beginning of the returned base URL.
        False to hide the "http(s)://" (so that "https://example.com/some/path" -> "example.com").

    Returns
    -------
    base_url : str
        Base URL.

    """
    # Function urlparse cannot parse a url if it does not start with http(s)://.
    # If such a url is passed, assume "http://".
    if not re.match("https?\:\/\/", url):
        warnings.warn(f"Schema not defined for url {url}; assuming http.")
        url = f"http://{url}"

    # Parse url, and return the base url either starting with "http(s)://" (if include_scheme is True) or without it.
    parsed_url = urlparse(url)
    if include_scheme:
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    else:
        base_url = parsed_url.netloc

    return base_url
