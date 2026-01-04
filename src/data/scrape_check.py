# -*- coding: utf-8 -*-
"""
Created on Sun Jul 27 21:40:37 2025

@author: Chris
"""

import requests

url = "https://www.fhwa.dot.gov/bridge/nbi/element.cfm"
resp = requests.get(url)

with open("element_raw.html", "w", encoding="utf-8") as f:
    f.write(resp.text)

print("Saved to element_raw.html")
