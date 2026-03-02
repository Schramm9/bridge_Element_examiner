# -*- coding: utf-8 -*-
"""
Created on Tue Dec 23 20:49:07 2025

@author: Chris
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parents[1] / "src"))


from from_fhwa.downloader import download_nbi_file

DATA_DIR = Path(__file__).parents[1] / "data"

# TEMPORARY: known FHWA URL (example)
url = "https://www.fhwa.dot.gov/bridge/nbi/2024/ca_element.zip"

out_dir = DATA_DIR / "raw" / "nbi" / "element" / "2024"

downloaded = download_nbi_file(
    url=url,
    out_dir=out_dir,
    filename="CA_2024_element.zip"
)

print(f"Downloaded to: {downloaded}")
