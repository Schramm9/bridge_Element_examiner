# -*- coding: utf-8 -*-

import json
from pathlib import Path

"""
Created on Sun Jan 11 15:41:05 2026

@author: Chris
"""

"""
FHWA NBI Element dataset discovery.

Scrapes:
- Landing page: https://www.fhwa.dot.gov/bridge/nbi/element.cfm
- Year pages:   https://www.fhwa.dot.gov/bridge/nbi/elementYYYY.cfm

Extracts element ZIP hrefs like:
- /bridge/nbi/element/2024/2024CA_ElementData.zip

Returns:
- list[StateDataset] with:
  state_abbr, year, dataset_type="bridge_element_data", url
"""

#from __future__ import annotations

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import re
from dataclasses import dataclass
from typing import Iterable
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from ..state_fips_rec import StateDataset  # per your package rule: no "src." imports elsewhere


BASE_URL = "https://www.fhwa.dot.gov/bridge/nbi/element.cfm"
DATASET_TYPE = "bridge_element_data"

# Some FHWA pages include 2-letter and occasionally 3-letter jurisdiction codes in filenames.
# Keep this permissive but still structured.
ZIP_RE = re.compile(r"(?P<year>\d{4})(?P<abbr>[A-Z]{2,3})_ElementData\.zip$", re.IGNORECASE)
YEAR_PAGE_RE = re.compile(r"element(?P<year>\d{4})\.cfm$", re.IGNORECASE)

DEFAULT_HEADERS = {
    "User-Agent": "bridge-element-examiner/1.0 (python-requests; contact: local)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

def _make_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=5,
        connect=5,
        read=5,
        backoff_factor=0.8,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update(DEFAULT_HEADERS)
    return session


_SESSION = _make_session()

def _get_soup(url: str, *, timeout: tuple[int, int] = (15, 90)) -> BeautifulSoup:
    # timeout = (connect_timeout, read_timeout)
    resp = _SESSION.get(url, timeout=timeout)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")



def _iter_year_page_urls(landing_url: str) -> list[str]:
    """
    From the landing page, return absolute URLs of year pages like:
    https://www.fhwa.dot.gov/bridge/nbi/element2024.cfm
    """
    soup = _get_soup(landing_url)

    year_urls: set[str] = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        m = YEAR_PAGE_RE.search(href)
        if not m:
            continue
        year_urls.add(urljoin(landing_url, href))

    # Sort newest-to-oldest by year in URL (stable, deterministic)
    def year_key(u: str) -> int:
        m2 = re.search(r"element(\d{4})\.cfm", u, re.IGNORECASE)
        return int(m2.group(1)) if m2 else -1

    return sorted(year_urls, key=year_key, reverse=True)


def _extract_zip_links_from_year_page(year_page_url: str) -> list[tuple[int, str, str]]:
    """
    Return tuples of (year, abbr, absolute_zip_url).
    """
    soup = _get_soup(year_page_url)

    out: list[tuple[int, str, str]] = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()

        # Only care about ElementData.zip downloads
        if "ElementData.zip" not in href:
            continue

        abs_zip_url = urljoin(year_page_url, href)
        filename = abs_zip_url.split("/")[-1]

        m = ZIP_RE.search(filename)
        if not m:
            # Still return it? In discovery we prefer to ignore unknown patterns
            # because we must populate state/year deterministically.
            continue

        year = int(m.group("year"))
        abbr = m.group("abbr").upper()

        out.append((year, abbr, abs_zip_url))

    # Deterministic ordering: year desc (though all same here), then abbr
    out.sort(key=lambda t: (t[0], t[1]))
    return out

def get_available_years(landing_url: str = BASE_URL) -> list[int]:
    """Return available 4-digit years found on the FHWA element landing page."""
    year_pages = _iter_year_page_urls(landing_url)
    years: list[int] = []
    for u in year_pages:
        m = YEAR_PAGE_RE.search(u)
        if m:
            years.append(int(m.group("year")))
    return sorted(set(years), reverse=True)

def discover_element_datasets(
    cache_path: Path | None = None,
    force: bool = False,
) -> list[StateDataset]:
    """
    Discover all available FHWA NBI Element ZIP datasets across all years.

    Parameters
    ----------
    cache_path : Path | None
        Optional path to a JSON cache file. If provided and the file exists
        (and force=False), discovery results are loaded from cache instead
        of hitting the FHWA website.
    force : bool
        If True, ignore any existing cache and re-run discovery.

    Returns
    -------
    list[StateDataset]
        Discovered element datasets (one per state per year).
    """

    # --- Load from cache if available ---
    if cache_path and cache_path.exists() and not force:
        data = json.loads(cache_path.read_text(encoding="utf-8"))
        return [StateDataset(**row) for row in data]

    datasets: list[StateDataset] = []

    # --- Discover year pages from landing page ---
    year_pages = _iter_year_page_urls(BASE_URL)

    seen: set[tuple[int, str]] = set()

    # --- Scrape each year page for ZIP links ---
    for year_page_url in year_pages:
        try:
            zip_rows = _extract_zip_links_from_year_page(year_page_url)
        except Exception as exc:
            # Discovery must be resilient — skip failed years, do not crash
            print(f"[WARN] Skipping year page due to error: {year_page_url} ({exc})")
            continue

        for year, state_abbr, zip_url in zip_rows:
            key = (year, state_abbr)
            if key in seen:
                continue
            seen.add(key)

            datasets.append(
                StateDataset(
                    state_abbr=state_abbr,
                    year=year,
                    dataset_type=DATASET_TYPE,  # "bridge_element_data"
                    url=zip_url,
                )
            )

    # --- Deterministic ordering ---
    datasets.sort(key=lambda d: (d.year, d.state_abbr), reverse=True)

    # --- Write cache if requested ---
    if cache_path:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(
            json.dumps([ds.__dict__ for ds in datasets], indent=2),
            encoding="utf-8",
        )

    return datasets
