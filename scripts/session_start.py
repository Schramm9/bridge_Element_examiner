# -*- coding: utf-8 -*-
"""
session_start.py

Run with F5 at the beginning of each Spyder session.

Purpose:
- Enable autoreload for package modules (src/)
- Lock project root + set working directory
- Ensure PROJECT_ROOT is on sys.path (for scripts and local runs)
- Create required data directories if missing
- Optional: initialize project logging (safe)
- Print session diagnostics + provide helpers
"""

from __future__ import annotations

from pathlib import Path
import os
import sys
import platform
import logging

DEV_MODE = True  # flip to False if you want quieter startup

# -------------------------------------------------
# 1) Enable autoreload (safe even if already loaded)
# -------------------------------------------------
try:
    from IPython import get_ipython
    ip = get_ipython()
    if ip is not None:
        ip.run_line_magic("load_ext", "autoreload")
        ip.run_line_magic("autoreload", "2")
except Exception:
    # Spyder sometimes runs without an IPython context during startup
    pass


# -------------------------------------------------
# 2) Define and lock PROJECT_ROOT
# -------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.chdir(PROJECT_ROOT)

# Ensure project root is importable (helps scripts/ + interactive dev)
root_str = str(PROJECT_ROOT)
if root_str not in sys.path:
    sys.path.insert(0, root_str)


# -------------------------------------------------
# 3) Ensure standard directory structure exists
# -------------------------------------------------
required_dirs = [
    PROJECT_ROOT / "data" / "raw",
    PROJECT_ROOT / "data" / "processed",
    PROJECT_ROOT / "data" / "interim",
    PROJECT_ROOT / "logs",
]
for d in required_dirs:
    d.mkdir(parents=True, exist_ok=True)


# -------------------------------------------------
# 4) Optional logging init (safe)
#    IMPORTANT: import via *package*, not via `src.`
# -------------------------------------------------
LOGGER = None
try:
    # Adjust this import to match your package layout.
    # If your installed package is "bridge_element_examiner", use that.
    from bridge_element_examiner.utils.logging_config import setup_logging  # type: ignore

    LOGGER = setup_logging(project_root=PROJECT_ROOT, level=logging.INFO)
    LOGGER.info("Session start complete.")
except Exception as e:
    # Don’t let logging failures break your whole dev session
    if DEV_MODE:
        print("[session_start] Logging not initialized (ok during dev). Reason:", repr(e))


# -------------------------------------------------
# 5) Helpers (pro workflow convenience)
# -------------------------------------------------
def project_info() -> None:
    """Print quick environment + path diagnostics."""
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

def ping_logger() -> None:
    """Confirm logging is working."""
    if LOGGER is None:
        print("LOGGER is not initialized.")
    else:
        LOGGER.info("Logger ping OK.")
        print("Logger ping sent.")

def restart_hint() -> None:
    """When autoreload isn't enough (rare), this reminds you what to do."""
    print("If changes aren't reflecting, do: Consoles → Restart kernel, then re-run session_start.py")


# -------------------------------------------------
# 6) Startup banner
# -------------------------------------------------
if DEV_MODE:
    project_info()
    print("Ready.")
    print("=" * 60)
