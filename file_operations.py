"""
file_operations.py
------------------
File-handling module for the Gym Management System.

Covers:
    - Part D: Export three attributes to CSV, import CSV back into a DataFrame.
    - Part E (partial): Save JSON outputs.
"""

# os is used to build file paths and create the exports/ folder.
import os
# json is Python's built-in JSON library — handles reading/writing JSON.
import json
# pandas for DataFrames and CSV I/O.
import pandas as pd
# Import the shared logger so file operations are logged.
from logger_config import log
# Import the function that reads members from the DB — used by the export.
from database import get_members_df

# Folder where all exported files (CSV, JSON) will be saved.
EXPORT_DIR = "exports"


# Private helper to ensure the exports/ folder exists before we write to it.
def _ensure_export_dir() -> None:
    # If the folder doesn't exist...
    if not os.path.exists(EXPORT_DIR):
        # ...create it. Prevents a crash on first run.
        os.makedirs(EXPORT_DIR)


# ---------------------------------------------------------------------------
# Part D — Export to CSV (three attributes)
# ---------------------------------------------------------------------------
# Export selected member attributes to a CSV file.
def export_members_to_csv(filename: str = "members_export.csv") -> str:
    """
    Export three attributes (name, membership_type, monthly_fee) from
    the members table into a CSV file.

    Returns the full path to the written file.
    """
    # Make sure the exports/ folder exists.
    _ensure_export_dir()
    # Build the full path: exports/members_export.csv (or whatever was passed).
    path = os.path.join(EXPORT_DIR, filename)
    # Try the export; if anything goes wrong, log and re-raise.
    try:
        # Read all members from the database into a DataFrame.
        df = get_members_df()
        # Pick exactly three attributes as required
        # Select exactly three columns — this is the Part D requirement.
        df_export = df[["name", "membership_type", "monthly_fee"]]
        # Write the DataFrame to CSV.
        # index=False stops pandas adding a leading column with row numbers.
        df_export.to_csv(path, index=False)
        # Log the number of rows written and where the file was saved.
        log.info(f"Exported {len(df_export)} rows to {path}")
        # Return the file path so the caller can show it to the user.
        return path
    # Catch KeyError (missing column) and OSError (disk/permission issues).
    except (KeyError, OSError) as e:
        log.error(f"Failed to export CSV: {e}")
        raise


# ---------------------------------------------------------------------------
# Part D — Import CSV back into a DataFrame
# ---------------------------------------------------------------------------
# Read the exported CSV back into a DataFrame — proves the round-trip works.
def import_members_from_csv(filename: str = "members_export.csv") -> pd.DataFrame:
    """Read the CSV back and return it as a DataFrame."""
    # Build the full path to the file.
    path = os.path.join(EXPORT_DIR, filename)
    # Try reading the CSV; handle the two main failure modes separately.
    try:
        # pd.read_csv parses the file and returns a DataFrame.
        df = pd.read_csv(path)
        # Log how many rows were imported.
        log.info(f"Imported {len(df)} rows from {path}")
        # Return the DataFrame.
        return df
    # The file doesn't exist at all — different from being empty.
    except FileNotFoundError:
        log.error(f"CSV file not found: {path}")
        raise
    # The file exists but has no parseable data — pandas-specific error.
    except pd.errors.EmptyDataError:
        log.error(f"CSV file is empty: {path}")
        raise


# ---------------------------------------------------------------------------
# JSON output helper (used by API module too)
# ---------------------------------------------------------------------------
# Save any dict or list to a pretty-printed JSON file.
# Used by both this module (for CSV-related JSON) and by api_integration.py.
def save_json(data: dict | list, filename: str) -> str:
    """Save a dict/list as a pretty-printed JSON file in exports/."""
    # Make sure exports/ exists.
    _ensure_export_dir()
    # Build the full file path.
    path = os.path.join(EXPORT_DIR, filename)
    # Try writing; catch OSError (disk) and TypeError (non-serialisable data).
    try:
        # Open the file for writing with UTF-8 encoding.
        # `with` is a context manager — guarantees the file closes even on error.
        with open(path, "w", encoding="utf-8") as f:
            # json.dump serialises the Python object and writes it to the file.
            # indent=4         → pretty-printed with 4-space indentation
            # ensure_ascii=False → keep non-ASCII characters as-is
            json.dump(data, f, indent=4, ensure_ascii=False)
        # Log where we saved it.
        log.info(f"Saved JSON output to {path}")
        # Return the path to the caller.
        return path
    # OSError = disk/permission issue. TypeError = data isn't serialisable.
    except (OSError, TypeError) as e:
        log.error(f"Failed to save JSON: {e}")
        raise