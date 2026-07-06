"""Shared logging configuration for the ETL pipeline scripts.

Both extract.py and load.py write to the same python/logs/pipeline.log file
and to stdout, so the setup lives here once instead of being duplicated.
"""

import logging
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"


def get_logger(name: str) -> logging.Logger:
    """Configure (once) and return a logger that writes to pipeline.log and stdout."""
    LOG_DIR.mkdir(exist_ok=True)

    root = logging.getLogger()
    if not root.handlers:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            handlers=[
                logging.FileHandler(LOG_DIR / "pipeline.log"),
                logging.StreamHandler(),
            ],
        )

    return logging.getLogger(name)
