# -*- coding: utf-8 -*-
"""
Created on Tue Dec  2 19:39:34 2025

@author: Chris
"""

import sys
from pathlib import Path

# Make project root importable
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))


from src.data.fhwa_scraper import FhwaScraper
import streamlit as st


def main():
    st.title("FHWA Element Data Downloader")

    scraper = FhwaScraper()

    st.write("🔍 Searching FHWA website for the latest available year...")

    try:
        year, state_links = scraper.get_available_states()
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return

    st.success(f"📅 Latest year with data: {year}")

    # Dropdown
    states = ["Select a state..."] + list(state_links.keys())
    selected_state = st.selectbox("Choose a State:", states)

    if selected_state != "Select a state...":
        st.write(f"⬇️ Download link for {selected_state}:")
        st.markdown(f"[Download ZIP file]({state_links[selected_state]})")


if __name__ == "__main__":
    main()
