# -*- coding: utf-8 -*-
"""
Created on Sun Dec 28 13:54:01 2025

@author: Chris
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


BASE_URL = "https://www.fhwa.dot.gov/bridge/nbi/"


def discover_nbi_zip_links(year: int, data_type: str) -> list[str]:
    """
    Discover FHWA NBI ZIP download URLs for a given year and data type.

    Parameters
    ----------
    year : int
        NBI data year (e.g., 2024)
    data_type : str
        One of {"element", "ascii"}

    Returns
    -------
    list[str]
        List of absolute ZIP URLs
    """

    if data_type not in {"element", "ascii"}:
        raise ValueError("data_type must be 'element' or 'ascii'")

    # Step 1: Build the year-specific page URL
    year_page = f"{BASE_URL}{data_type}{year}.cfm"

    response = requests.get(year_page, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    zip_links = []

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if href.lower().endswith(".zip"):
            full_url = urljoin(BASE_URL, href)
            zip_links.append(full_url)

    return sorted(set(zip_links))
