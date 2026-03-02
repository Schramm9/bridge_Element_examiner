from pathlib import Path
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 15 12:40:55 2026

@author: Chris
"""

"""
Bulk-download all discovered FHWA NBI ASCII datasets (no delimiter / fixed-width).

Usage:
    python scripts/download_all_ascii.py
"""


from data.download_data import download_dataset
from from_fhwa.discovery.disc_ascii_links import discover_ascii_datasets


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    data_root = project_root / "data" / "raw"

    datasets = discover_ascii_datasets()
    print(f"Discovered {len(datasets)} ASCII datasets.")

    downloaded = 0
    skipped = 0
    failed = 0

    for ds in datasets:
        try:
            result = download_dataset(ds, data_root=data_root)
            downloaded += 1
            print(f"[OK] {ds.year} {ds.state_abbr} -> {result}")

        except FileExistsError:
            skipped += 1
            print(f"[SKIP] {ds.year} {ds.state_abbr} (already exists)")

        except Exception as e:
            failed += 1
            print(f"[FAIL] {ds.year} {ds.state_abbr}: {e}")

    print("\nSummary")
    print(f"  downloaded: {downloaded}")
    print(f"  skipped:    {skipped}")
    print(f"  failed:     {failed}")


if __name__ == "__main__":
    main()
