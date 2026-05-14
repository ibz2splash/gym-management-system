"""
file_operations.py
------------------
File-handling module for the Gym Management System.

Covers:
    - Part D: Export three attributes to CSV, import CSV back into a DataFrame.
    - Part E (partial): Save JSON outputs.
"""

import os
import json
import pandas as pd
from logger_config import log
from database import get_members_df

EXPORT_DIR = "exports"


def _ensure_export_dir() -> None:
    if not os.path.exists(EXPORT_DIR):
        os.makedirs(EXPORT_DIR)


# ---------------------------------------------------------------------------
# Part D — Export to CSV (three attributes)
# ---------------------------------------------------------------------------
def export_members_to_csv(filename: str = "members_export.csv") -> str:
    """
    Export three attributes (name, membership_type, monthly_fee) from
    the members table into a CSV file.

    Returns the full path to the written file.
    """
    _ensure_export_dir()
    path = os.path.join(EXPORT_DIR, filename)
    try:
        df = get_members_df()
        # Pick exactly three attributes as required
        df_export = df[["name", "membership_type", "monthly_fee"]]
        df_export.to_csv(path, index=False)
        log.info(f"Exported {len(df_export)} rows to {path}")
        return path
    except (KeyError, OSError) as e:
        log.error(f"Failed to export CSV: {e}")
        raise


# ---------------------------------------------------------------------------
# Part D — Import CSV back into a DataFrame
# ---------------------------------------------------------------------------
def import_members_from_csv(filename: str = "members_export.csv") -> pd.DataFrame:
    """Read the CSV back and return it as a DataFrame."""
    path = os.path.join(EXPORT_DIR, filename)
    try:
        df = pd.read_csv(path)
        log.info(f"Imported {len(df)} rows from {path}")
        return df
    except FileNotFoundError:
        log.error(f"CSV file not found: {path}")
        raise
    except pd.errors.EmptyDataError:
        log.error(f"CSV file is empty: {path}")
        raise


# ---------------------------------------------------------------------------
# JSON output helper (used by API module too)
# ---------------------------------------------------------------------------
def save_json(data: dict | list, filename: str) -> str:
    """Save a dict/list as a pretty-printed JSON file in exports/."""
    _ensure_export_dir()
    path = os.path.join(EXPORT_DIR, filename)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        log.info(f"Saved JSON output to {path}")
        return path
    except (OSError, TypeError) as e:
        log.error(f"Failed to save JSON: {e}")
        raise
