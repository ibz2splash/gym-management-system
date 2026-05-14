"""
api_integration.py
------------------
Public API integration module.

API used: Wger Workout Manager (https://wger.de/api/v2/)
    - Free, public, no authentication required.
    - Returns exercise / fitness data — perfect for a Gym Management System.

Covers Part E:
    1. API integration
    2. Fetch data from public API
    3. Store it in the database (a small reference table)
    4. Provide output in JSON format
    5. Proper error handling
"""

import sqlite3
import requests
from logger_config import log
from database import get_connection
from file_operations import save_json

WGER_BASE_URL = "https://wger.de/api/v2"
TIMEOUT_SECONDS = 10
HEADERS = {
    "User-Agent": "GymManagementSystem/1.0 (Educational Project)",
    "Accept": "application/json",
}


# ---------------------------------------------------------------------------
# Helper: create a small reference table for API-fetched exercises
# ---------------------------------------------------------------------------
def _ensure_api_exercises_table() -> None:
    """Create a table to store exercises fetched from the API."""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS api_exercises (
                api_id      INTEGER PRIMARY KEY,
                name        TEXT,
                category_id INTEGER
            );
            """
        )
        conn.commit()


# ---------------------------------------------------------------------------
# Fetch from API
# ---------------------------------------------------------------------------
def fetch_exercises(limit: int = 20) -> list[dict]:
    """
    Fetch a list of exercises from the Wger API.

    Returns a list of dicts with id, name, category.
    Includes full error handling for network / HTTP / JSON failures.
    """
    url = f"{WGER_BASE_URL}/exerciseinfo/?language=2&limit={limit}"
    log.info(f"Calling Wger API: {url}")
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()  # raises HTTPError for 4xx/5xx
        data = response.json()
    except requests.exceptions.Timeout:
        log.error("API request timed out.")
        return []
    except requests.exceptions.ConnectionError:
        log.error("Could not connect to the API (network issue).")
        return []
    except requests.exceptions.HTTPError as e:
        log.error(f"HTTP error from API: {e}")
        return []
    except ValueError:  # JSON decoding error
        log.error("API returned invalid JSON.")
        return []

    results = data.get("results", [])
    log.info(f"API returned {len(results)} raw exercise records.")

    # Normalize: keep only the fields we care about
    exercises = []
    for item in results:
        # `name` lives inside translations; pick the English one if available
        name = None
        for tr in item.get("translations", []):
            if tr.get("language") == 2:  # 2 = English
                name = tr.get("name")
                break
        if not name:
            continue  # skip records without an English name

        exercises.append({
            "api_id": item.get("id"),
            "name": name,
            "category_id": (item.get("category") or {}).get("id"),
        })

    log.info(f"Parsed {len(exercises)} usable exercises from API.")
    return exercises


# ---------------------------------------------------------------------------
# Store API data in the database
# ---------------------------------------------------------------------------
def store_exercises_in_db(exercises: list[dict]) -> int:
    """Insert API-fetched exercises into the api_exercises table."""
    if not exercises:
        log.error("No exercises to store — list is empty.")
        return 0

    _ensure_api_exercises_table()
    inserted = 0
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            for ex in exercises:
                cur.execute(
                    """INSERT OR REPLACE INTO api_exercises
                       (api_id, name, category_id) VALUES (?, ?, ?);""",
                    (ex["api_id"], ex["name"], ex["category_id"]),
                )
                inserted += 1
            conn.commit()
        log.info(f"Stored {inserted} exercises into api_exercises table.")
    except sqlite3.Error as e:
        log.error(f"Database error while storing API data: {e}")
    return inserted


# ---------------------------------------------------------------------------
# Full workflow: fetch -> store -> JSON output
# ---------------------------------------------------------------------------
def run_api_workflow(limit: int = 20) -> str:
    """
    End-to-end:
        1. Fetch exercises
        2. Store in DB
        3. Save JSON output
    Returns the path of the JSON output file.
    """
    exercises = fetch_exercises(limit=limit)
    store_exercises_in_db(exercises)
    json_path = save_json(exercises, "exercises_output.json")
    return json_path
