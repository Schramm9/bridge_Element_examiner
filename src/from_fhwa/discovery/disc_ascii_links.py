from __future__ import annotations
import json
from pathlib import Path

# -*- coding: utf-8 -*-
"""
Created on Sun Jan 11 15:42:11 2026

@author: Chris
"""

"""
FHWA NBI ASCII dataset discovery.

Scrapes:
- Landing page: https://www.fhwa.dot.gov/bridge/nbi/ascii.cfm
- Year pages:   https://www.fhwa.dot.gov/bridge/nbi/asciiYYYY.cfm

Year pages contain state links that go through a disclaimer:
- disclaim.cfm?nbiState=CA25&nbiYear=2025

We bypass the disclaimer and build the direct TXT URL:
- https://www.fhwa.dot.gov/bridge/nbi/2025/CA25.txt

(Delimited variants exist too: /2025/delimited/CA25.txt — not included here by default.)
"""

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


import re
from urllib.parse import parse_qs, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from from_fhwa.state_fips_rec import StateDataset


BASE_URL = "https://www.fhwa.dot.gov/bridge/nbi/ascii.cfm"
DATASET_TYPE = "ascii"

YEAR_PAGE_RE = re.compile(r"ascii(?P<year>\d{4})\.cfm$", re.IGNORECASE)

DEFAULT_HEADERS = {
    "User-Agent": "bridge-element-examiner/1.0 (python-requests)",
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
    soup = _get_soup(landing_url)

    year_urls: set[str] = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if YEAR_PAGE_RE.search(href):
            year_urls.add(urljoin(landing_url, href))

    def year_key(u: str) -> int:
        m = re.search(r"ascii(\d{4})\.cfm", u, re.IGNORECASE)
        return int(m.group(1)) if m else -1

    return sorted(year_urls, key=year_key, reverse=True)


def _dataset_from_disclaimer_link(year_page_url: str, href: str) -> StateDataset | None:
    """
    Convert disclaimer link:
      disclaim.cfm?nbiState=CA25&nbiYear=2025
    into direct file URL:
      https://www.fhwa.dot.gov/bridge/nbi/2025/CA25.txt
    """
    abs_url = urljoin(year_page_url, href)
    parsed = urlparse(abs_url)
    qs = parse_qs(parsed.query)

    nbi_state = (qs.get("nbiState") or [None])[0]
    nbi_year = (qs.get("nbiYear") or [None])[0]
    if not nbi_state or not nbi_year:
        return None

    # nbi_state is like "CA25" (letters + 2-digit year suffix)
    # keep letters only as the jurisdiction abbreviation
    state_abbr = "".join([c for c in nbi_state if c.isalpha()]).upper()

    # nbi_year is like "2025" or "2025/delimited"
    year_str = nbi_year.split("/")[0]
    if not year_str.isdigit():
        return None
    year = int(year_str)

    # Only include "no delimiter" (fixed-width) by default:
    # If nbi_year contains "/delimited", skip it here.
    if "/delimited" in nbi_year.lower():
        return None

    txt_url = f"https://www.fhwa.dot.gov/bridge/nbi/{year}/{nbi_state}.txt"

    return StateDataset(
        state_abbr=state_abbr,
        year=year,
        dataset_type=DATASET_TYPE,
        url=txt_url,
    )


def discover_ascii_datasets(cache_path: Path | None = None, force: bool = False) -> list[StateDataset]:
    if cache_path and cache_path.exists() and not force:
        data = json.loads(cache_path.read_text(encoding="utf-8"))
        return [StateDataset(**row) for row in data]
    datasets: list[StateDataset] = []

    year_pages = _iter_year_page_urls(BASE_URL)
    seen: set[tuple[int, str]] = set()

    for year_page_url in year_pages:
        soup = _get_soup(year_page_url)
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if "disclaim.cfm" not in href:
                continue

            ds = _dataset_from_disclaimer_link(year_page_url, href)
            if not ds:
                continue

            key = (ds.year, ds.state_abbr)
            if key in seen:
                continue
            seen.add(key)
            datasets.append(ds)

    datasets.sort(key=lambda d: (d.year, d.state_abbr), reverse=True)

    if cache_path:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(
            json.dumps([ds.__dict__ for ds in datasets], indent=2),
            encoding="utf-8",
        )
    return datasets
