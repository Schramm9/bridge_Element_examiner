# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 20:19:59 2026

@author: Chris
"""

"""
session_start.py

Run this at the beginning of each Spyder session.

Purpose:
- Enable autoreload for src/ modules
- Lock project root
- Ensure project root is on sys.path
- Confirm environment + working directory
- Create required data directories if missing
"""



from pathlib import Path
import sys
import platform


# -------------------------------------------------
# 1️⃣ Enable autoreload (safe even if already loaded)
# -------------------------------------------------
try:
    from IPython import get_ipython
    ip = get_ipython()
    if ip is not None:
        ip.run_line_magic("load_ext", "autoreload")
        ip.run_line_magic("autoreload", "2")
except Exception:
    pass


# -------------------------------------------------
# 2️⃣ Define and lock PROJECT_ROOT
# -------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]

import os
os.chdir(PROJECT_ROOT)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# -------------------------------------------------
# 3️⃣ Ensure standard directory structure exists
# -------------------------------------------------
required_dirs = [
    PROJECT_ROOT / "data" / "raw",
    PROJECT_ROOT / "data" / "processed",
    PROJECT_ROOT / "logs",
]

for d in required_dirs:
    d.mkdir(parents=True, exist_ok=True)


# -------------------------------------------------
# 4️⃣ Session diagnostics
# -------------------------------------------------
print("=" * 60)
print("FHWA PROJECT SESSION INITIALIZED")
print("=" * 60)
print("Project Root:", PROJECT_ROOT)
print("Working Dir :", Path.cwd())
print("Python      :", sys.executable)
print("Platform    :", platform.platform())
print("Autoreload  : Enabled (mode 2)")
print("sys.path[0] :", sys.path[0])
print("=" * 60)
print("Ready.")
print("=" * 60)
