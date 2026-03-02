# -*- coding: utf-8 -*-
"""
Created on Sun Dec 28 14:33:06 2025

@author: Chris
"""

import requests
from bs4 import BeautifulSoup

url = "https://www.fhwa.dot.gov/bridge/nbi/element2024.cfm"

response = requests.get(url)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

print("ZIP links found:\n")

for a in soup.find_all("a", href=True):
    if a["href"].lower().endswith(".zip"):
        print(a["href"])
