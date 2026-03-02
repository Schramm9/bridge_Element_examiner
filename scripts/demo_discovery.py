# -*- coding: utf-8 -*-
"""
Created on Sun Dec 28 13:54:44 2025

@author: Chris
"""

import sys
from pathlib import Path

# Add src/ to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

from from_fhwa.discovery import discover_nbi_zip_links
import requests
from bs4 import BeautifulSoup

url = "https://www.fhwa.dot.gov/bridge/nbi/element.cfm"

html = requests.get(url).text
soup = BeautifulSoup(html, "html.parser")

print("All links found:\n")

for a in soup.find_all("a", href=True):
    print(a["href"])
