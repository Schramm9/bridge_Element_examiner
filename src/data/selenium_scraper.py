# -*- coding: utf-8 -*-
"""
Created on Sat Aug  2 19:09:06 2025

@author: Chris
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import os

def _init_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=options)

def get_available_states_selenium():
    driver = _init_driver()
    driver.get(BASE_ELEMENT_URL)
    time.sleep(2)  # allow JS to render

    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Find the first link containing a 4-digit year and click it
    year_link = driver.find_element("xpath", "//a[contains(text(), '202')]")
    latest_year = year_link.text.strip()
    year_link.click()
    time.sleep(2)

    soup2 = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    # Now find all ZIP links inside the content area
    links = soup2.select("a[href$='.zip']")
    state_links = {
        a.get_text(strip=True): urljoin(BASE_ELEMENT_URL, a["href"])
        for a in links if len(a.get_text(strip=True)) > 2
    }

    print(f"✅ States found for {latest_year}: {list(state_links.keys())}")
    return latest_year, state_links
