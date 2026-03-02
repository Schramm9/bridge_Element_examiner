"""
download_test_ca_2024.py

Fast-path direct download + unzip for FHWA NBI Element data (CA, 2024).

Designed to be run inside Spyder so variables are visible in Variable Explorer.
- Downloads the ZIP to data/raw/nbi/element/2024/
- Verifies it's a real ZIP
- Extracts it to a sibling folder named after the ZIP stem
- Locates the main XML file (expected: 2024CA_ElementData.xml)
"""

from __future__ import annotations

from pathlib import Path
import zipfile
import requests


# -----------------------------
# USER SETTINGS (edit if needed)
# -----------------------------
YEAR = 2024
STATE_ABBR = "CA"

# IMPORTANT: set this to your actual project root
PROJECT_ROOT = Path(r"C:\Users\Chris\CodingBootcamp\Homework\bridge_element_examiner")


# -----------------------------
# DERIVED PATHS / URL
# -----------------------------
url = f"https://www.fhwa.dot.gov/bridge/nbi/element/{YEAR}/{YEAR}{STATE_ABBR}_ElementData.zip"

outdir = PROJECT_ROOT / "data" / "raw" / "nbi" / "element" / str(YEAR)
outdir.mkdir(parents=True, exist_ok=True)

zip_path = outdir / f"{YEAR}{STATE_ABBR}_ElementData.zip"

extract_dir = outdir / f"{YEAR}{STATE_ABBR}_ElementData"
extract_dir.mkdir(parents=True, exist_ok=True)

headers = {"User-Agent": "Mozilla/5.0"}  # helps avoid some basic blocks


# -----------------------------
# DOWNLOAD
# -----------------------------
# Tip for Spyder: run selection or run file in "current console"
# so variables show up in Variable Explorer.

resp = requests.get(url, stream=True, headers=headers, timeout=120, allow_redirects=True)

status_code = resp.status_code
content_type = resp.headers.get("Content-Type")
final_url = resp.url

print("Request status:", status_code)
print("Content-Type:", content_type)
print("Final URL:", final_url)

if status_code != 200:
    raise RuntimeError(f"Download failed with HTTP {status_code}: {final_url}")

# Write file to disk
with open(zip_path, "wb") as f:
    for chunk in resp.iter_content(chunk_size=1024 * 1024):
        if chunk:
            f.write(chunk)

zip_size = zip_path.stat().st_size
print("Saved ZIP:", zip_path)
print("ZIP size (bytes):", zip_size)

# Verify it's a zip
is_zip = zipfile.is_zipfile(zip_path)
print("Is valid zip?:", is_zip)
if not is_zip:
    # Helpful debugging: show first bytes to see if HTML was saved as .zip
    with open(zip_path, "rb") as f:
        head = f.read(200)
    raise RuntimeError(
        "File is not a valid ZIP. First bytes:\n"
        f"{head!r}\n\n"
        "Likely downloaded an HTML page instead of a zip."
    )


# -----------------------------
# EXTRACT
# -----------------------------
with zipfile.ZipFile(zip_path, "r") as z:
    z.extractall(extract_dir)

print("Extracted to:", extract_dir)

# List extracted top-level contents
top_level = sorted([p.name for p in extract_dir.iterdir()])
print("Top-level extracted items:", top_level)

# Find XML file(s)
xml_files = list(extract_dir.rglob("*.xml"))
print("XML files found:", [str(p) for p in xml_files])

if not xml_files:
    raise RuntimeError("No .xml files found after extraction.")

# Prefer the expected main file if present; else take largest XML
expected = extract_dir / f"{YEAR}{STATE_ABBR}_ElementData.xml"
if expected.exists():
    xml_main = expected
else:
    xml_main = sorted(xml_files, key=lambda p: p.stat().st_size, reverse=True)[0]

print("Selected XML:", xml_main)
print("Selected XML size (bytes):", xml_main.stat().st_size)

# Print first few lines for quick sanity check
with open(xml_main, "r", encoding="utf-8", errors="replace") as f:
    print("\n--- XML HEAD (first 15 lines) ---")
    for _ in range(15):
        print(f.readline().rstrip())
