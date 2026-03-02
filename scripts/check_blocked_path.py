# -*- coding: utf-8 -*-
"""
Created on Sat Jan  3 17:40:19 2026

@author: Chris
"""

import subprocess
import sys
#from pathlib import Path

BLOCKED_PREFIXES = (
    "data/raw/",
    "data/processed/",
    "cache/",
)

def main():
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
    )

    files = result.stdout.splitlines()
    offenders = [f for f in files if f.startswith(BLOCKED_PREFIXES)]

    if offenders:
        print("❌ Blocked staged files detected:\n")
        for f in offenders:
            print(f"  - {f}")
        print("\nRemove these from the commit or update .gitignore.")
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()
