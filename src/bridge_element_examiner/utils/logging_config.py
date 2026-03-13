# -*- coding: utf-8 -*-
"""
Created on Tue Mar  3 11:39:05 2026

@author: Chris
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(
    *,
    project_root: Path,
    log_name: str = "fhwa",
    level: int = logging.INFO,
    console: bool = True,
) -> logging.Logger:
    """
    Configure logging for the project.

    - Writes rotating logs to {project_root}/logs/{log_name}.log
    - Optionally logs to console as well
    - Safe to call multiple times (won't duplicate handlers)
    """
    logs_dir = project_root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(log_name)
    logger.setLevel(level)
    logger.propagate = False  # prevent double logging via root logger

    # Avoid duplicate handlers if this is called multiple times
    if getattr(logger, "_is_configured", False):
        return logger

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        filename=str(logs_dir / f"{log_name}.log"),
        maxBytes=5_000_000,  # 5 MB
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(fmt)
        logger.addHandler(console_handler)

    logger._is_configured = True
    logger.info("Logging initialized.")
    return logger
