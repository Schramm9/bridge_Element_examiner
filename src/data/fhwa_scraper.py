# -*- coding: utf-8 -*-
"""
Created on Tue Dec  2 19:00:09 2025

@author: Chris
"""

# src/data/fhwa_scraper.py
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.fhwa.dot.gov/bridge/nbi"


class FhwaScraper:
    """
    Scrapes FHWA NBI Element Data (and later ASCII data) without Selenium.
    Automatically finds the most recent year that contains valid state ZIP links.
    """

    def __init__(self):
        self.session = requests.Session()

    def _fetch_html(self, url):
        """Fetch HTML and return BeautifulSoup object."""
        response = self.session.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    def _extract_state_links(self, soup):
        """
        Given a BeautifulSoup object for an elementYYYY.cfm page,
        extract all state download ZIP links.
        Returns: dict { "StateName": "URL.zip" }
        """
        links = {}

        # All ZIP links look like: /bridge/nbi/element/2024/2024CA_ElementData.zip
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "ElementData.zip" in href:
                state_name = a.text.strip()
                full_url = href if href.startswith("http") else BASE_URL + "/" + href.lstrip("/")
                links[state_name] = full_url

        return links

    def get_latest_year_with_data(self, start=2025, end=2010):
        """
        Try each year from newest → oldest and return the first
        year containing valid ZIP links.
        """
        for year in range(start, end - 1, -1):
            url = f"{BASE_URL}/element{year}.cfm"
            print(f"Checking {url} ...")

            try:
                soup = self._fetch_html(url)
                state_links = self._extract_state_links(soup)

                if state_links:
                    print(f"✔ Found {len(state_links)} states for {year}")
                    return year, state_links

            except Exception as e:
                print(f"⚠ Error reading {year}: {e}")

        raise ValueError("❌ No FHWA element data found for any year in the provided range.")

    def get_available_states(self):
        """
        Returns:
            year (int)
            state_links: dict {state_name → download_url}
        """
        year, links = self.get_latest_year_with_data()
        return year, links
