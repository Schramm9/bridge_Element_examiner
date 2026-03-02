# -*- coding: utf-8 -*-
"""
Created on Mon Jan 19 18:42:26 2026

@author: Chris
"""

from pathlib import Path

from data.extract_element_zips import extract_all_element_zips
from data.parse_element_xml import parse_element_xml_batch


def main():
    project_root = Path(__file__).resolve().parents[1]
    data_root = project_root / "data" / "raw"
    interim_root = project_root / "data" / "interim"

    # Pilot: only CA, only two years (edit as needed)
    results = extract_all_element_zips(
        data_root=data_root,
        interim_root=interim_root,
        state_abbr="CA",
        years={2025, 2020},
        overwrite=False,
    )

    print(f"ZIPs: {len(results)}")
    print(f"Extracted: {sum(not r.skipped for r in results)}  Skipped: {sum(r.skipped for r in results)}")

    df = parse_element_xml_batch(interim_root=interim_root, state_abbr="CA", years={2025, 2020})
    print(df.head(10))
    print("Rows:", len(df))


if __name__ == "__main__":
    main()
