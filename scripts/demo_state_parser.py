# -*- coding: utf-8 -*-
"""
Created on Sun Dec 28 14:25:35 2025

@author: Chris
"""

from from_fhwa.discovery import discover_nbi_zip_links
from from_fhwa.state_parser import parse_state_from_zip_url

links = discover_nbi_zip_links(2024, "element")

parsed = []

for link in links:
    info = parse_state_from_zip_url(link)
    if info:
        parsed.append(info)

print(f"Parsed {len(parsed)} state entries:\n")

for item in parsed[:10]:  # show first 10
    print(item)
