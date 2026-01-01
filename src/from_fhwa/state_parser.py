# -*- coding: utf-8 -*-
"""
Created on Sun Dec 28 14:24:23 2025

@author: Chris
"""

import re
from urllib.parse import urlparse
from pathlib import Path


STATE_FILE_PATTERN = re.compile(
    r"^(?P<state>[A-Z]{2})_(?P<type>Element|ASCII)\.zip$"
)


def parse_state_from_zip_url(url: str) -> dict | None:
    """
    Extract state identifier and metadata from an FHWA NBI ZIP URL.

    Parameters
    ----------
    url : str
        FHWA ZIP download URL

    Returns
    -------
    dict | None
        Dictionary with parsed metadata, or None if pattern does not match
    """

    parsed = urlparse(url)
    filename = Path(parsed.path).name

    match = STATE_FILE_PATTERN.match(filename)
    if not match:
        return None

    return {
        "state_code": match.group("state"),
        "data_type": match.group("type").lower(),
        "filename": filename,
        "url": url,
    }
