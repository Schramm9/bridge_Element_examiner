from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import requests
from pathlib import Path

BASE_ELEMENT_URL = "https://www.fhwa.dot.gov/bridge/nbi/element.cfm"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw" / "element"

def _init_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    service = Service('./bin/chromedriver.exe')
    return webdriver.Chrome(service=service, options=options)

def get_available_states():
    """Uses Selenium to extract the list of available state names from the latest year."""
    driver = _init_driver()
    driver.get(BASE_ELEMENT_URL)

    try:
        # Wait for the unordered list of year links to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//ul//a[contains(@href, '.cfm') and contains(@href, '20')]"))
        )
    except Exception as e:
        driver.quit()
        raise RuntimeError(f"❌ Failed to locate year links: {e}")

    # Extract all <a> tags that link to yearly pages
    year_links = driver.find_elements(By.XPATH, "//ul//a[contains(@href, '.cfm') and contains(@href, '20')]")
    print("Found year links:")
    for link in year_links:
        print(" •", link.get_attribute("href"))

    if not year_links:
        driver.quit()
        raise ValueError("❌ Could not find any year links.")

    # Click the first (most recent) year link
    state_map = {}

    for link in year_links:
        year_url = link.get_attribute("href")
        driver.get(year_url)
        time.sleep(2)

    state_links = driver.find_elements(By.XPATH, "//ul//a[contains(@href, '.xml')]")
    if state_links:
        print(f"\n✅ Found state links on: {year_url}")
        for state_link in state_links:
            state_name = state_link.text.strip()
            state_url = state_link.get_attribute("href")
            if state_name and state_url:
                state_map[state_name] = state_url
        break  # Stop after first year with data
    else:
        print(f"⚠️ No state links found on: {year_url}, trying next year...")

    time.sleep(2)

    # Scrape all state links (usually .xml files)
    state_links = driver.find_elements(By.XPATH, "//ul//a[contains(@href, '.xml')]")
    print("\nFound state links:")
    state_map = {}

    for link in state_links:
        state_name = link.text.strip()
        state_url = link.get_attribute("href")
        print(f" • {state_name} -> {state_url}")
        if state_name and state_url:
            state_map[state_name] = state_url

    driver.quit()

    if not state_map:
        raise ValueError("❌ Could not find any state download links.")

    return list(state_map.keys())

def download_state_data(state_name):
    """Download all available element data for a selected state across years."""
    driver = _init_driver()
    driver.get(BASE_ELEMENT_URL)
    time.sleep(2)

    # Get all year links from the main page
    year_links = driver.find_elements(By.XPATH, "//a[contains(@href, 'element.cfm') and contains(text(), '20')]")
    if not year_links:
        driver.quit()
        raise ValueError("❌ No year links found.")

    years_and_urls = [(link.text.strip(), link.get_attribute("href")) for link in year_links]

    downloaded = []

    for year, url in years_and_urls:
        driver.get(url)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        links = soup.select("a[href$='.zip']")
        state_links = {
            a.get_text(strip=True): urljoin(url, a["href"])
            for a in links if len(a.get_text(strip=True)) > 2
        }

        if state_name in state_links:
            download_url = state_links[state_name]
            filename = f"{state_name.replace(' ', '_')}_{year}.zip"
            filepath = RAW_DATA_DIR / filename
            RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

            response = requests.get(download_url)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"✅ Downloaded {filename}")
            downloaded.append(filename)
        else:
            print(f"⚠️ {state_name} not found for year {year}")

    driver.quit()

    if not downloaded:
        raise ValueError(f"❌ No data found for {state_name} in any year.")

    return downloaded
