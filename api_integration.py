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

# sqlite3 for catching database-specific errors during the store step.
import sqlite3
# requests is the standard HTTP library — sends the GET request to Wger.
import requests
# Shared logger from logger_config.
from logger_config import log
# Reuse the database connection function — modular architecture in action.
from database import get_connection
# Reuse the JSON-writing helper from file_operations.
from file_operations import save_json

# The base URL of the Wger API. Everything else is appended to this.
WGER_BASE_URL = "https://wger.de/api/v2"
# Maximum seconds to wait for a response before giving up.
# Without a timeout, a slow server could freeze the program forever.
TIMEOUT_SECONDS = 10
# HTTP headers sent with every request.
# User-Agent identifies our app politely; Accept tells the server we want JSON.
HEADERS = {
    "User-Agent": "GymManagementSystem/1.0 (Educational Project)",
    "Accept": "application/json",
}


# ---------------------------------------------------------------------------
# Helper: create a small reference table for API-fetched exercises
# ---------------------------------------------------------------------------
# Make sure the api_exercises table exists before we try to store data in it.
def _ensure_api_exercises_table() -> None:
    """Create a table to store exercises fetched from the API."""
    # Open the database connection.
    with get_connection() as conn:
        # CREATE TABLE IF NOT EXISTS is safe to run repeatedly.
        # api_id is the PK — it's the ID assigned by the Wger API itself.
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS api_exercises (
                api_id      INTEGER PRIMARY KEY,
                name        TEXT,
                category_id INTEGER
            );
            """
        )
        # Persist the schema change.
        conn.commit()


# ---------------------------------------------------------------------------
# Fetch from API
# ---------------------------------------------------------------------------
# Send a GET request to Wger and return the parsed exercises.
def fetch_exercises(limit: int = 20) -> list[dict]:
    """
    Fetch a list of exercises from the Wger API.

    Returns a list of dicts with id, name, category.
    Includes full error handling for network / HTTP / JSON failures.
    """
    # Build the URL with query parameters: language=2 (English), and the limit.
    url = f"{WGER_BASE_URL}/exerciseinfo/?language=2&limit={limit}"
    # Log the call so we can see in the log file exactly what URL was requested.
    log.info(f"Calling Wger API: {url}")
    # Try the request; each failure mode is caught separately below.
    try:
        # Send the GET request with our headers and timeout.
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT_SECONDS)
        # If the response status is 4xx or 5xx, raise HTTPError.
        # Without this, a 404 page would be treated as a valid response.
        response.raise_for_status()  # raises HTTPError for 4xx/5xx
        # Parse the response body as JSON — turns it into a Python dict.
        data = response.json()
    # Server didn't respond within TIMEOUT_SECONDS.
    except requests.exceptions.Timeout:
        log.error("API request timed out.")
        # Return empty list so the program can continue gracefully.
        return []
    # No internet, DNS failure, or server unreachable.
    except requests.exceptions.ConnectionError:
        log.error("Could not connect to the API (network issue).")
        return []
    # Server returned 4xx or 5xx (caught by raise_for_status above).
    except requests.exceptions.HTTPError as e:
        log.error(f"HTTP error from API: {e}")
        return []
    # Response succeeded but the body isn't valid JSON.
    except ValueError:  # JSON decoding error
        log.error("API returned invalid JSON.")
        return []

    # data["results"] is where Wger puts the list of exercises.
    # .get() with default [] is defensive — won't crash if key is missing.
    results = data.get("results", [])
    # Log how many raw records came back.
    log.info(f"API returned {len(results)} raw exercise records.")

    # Normalize: keep only the fields we care about
    # Build a clean list of dicts with just the three fields we need.
    exercises = []
    # Loop through each raw exercise from the API.
    for item in results:
        # `name` lives inside translations; pick the English one if available
        # Wger stores exercise names inside a 'translations' array because
        # the API supports multiple languages.
        name = None
        # Loop through every translation to find the English one.
        for tr in item.get("translations", []):
            # Language ID 2 = English in Wger's system.
            if tr.get("language") == 2:  # 2 = English
                # Got the English name — save it and stop looking.
                name = tr.get("name")
                break
        # If no English translation exists, skip this exercise entirely.
        if not name:
            continue  # skip records without an English name

        # Append a clean dict with just our three fields.
        # (item.get("category") or {}) is defensive — if category is None,
        # we substitute an empty dict so the next .get() doesn't crash.
        exercises.append({
            "api_id": item.get("id"),
            "name": name,
            "category_id": (item.get("category") or {}).get("id"),
        })

    # Log how many usable exercises we ended up with.
    log.info(f"Parsed {len(exercises)} usable exercises from API.")
    # Return the clean list to the caller.
    return exercises


# ---------------------------------------------------------------------------
# Store API data in the database
# ---------------------------------------------------------------------------
# Take the list of parsed exercises and insert them into the database.
def store_exercises_in_db(exercises: list[dict]) -> int:
    """Insert API-fetched exercises into the api_exercises table."""
    # If the list is empty (e.g. API call failed), don't even try.
    if not exercises:
        log.error("No exercises to store — list is empty.")
        return 0

    # Make sure the api_exercises table exists.
    _ensure_api_exercises_table()
    # Counter for how many rows we successfully insert.
    inserted = 0
    # Try the bulk insert; catch any SQLite errors.
    try:
        # Open the DB connection.
        with get_connection() as conn:
            # Get a cursor for executing SQL.
            cur = conn.cursor()
            # Loop over each exercise and insert it.
            for ex in exercises:
                # INSERT OR REPLACE is SQLite-specific — if a row with the
                # same api_id already exists, replace it. This means we can
                # call the API multiple times without creating duplicates.
                cur.execute(
                    """INSERT OR REPLACE INTO api_exercises
                       (api_id, name, category_id) VALUES (?, ?, ?);""",
                    (ex["api_id"], ex["name"], ex["category_id"]),
                )
                # Track how many we've inserted.
                inserted += 1
            # Persist all the inserts in one commit.
            conn.commit()
        # Log the total count.
        log.info(f"Stored {inserted} exercises into api_exercises table.")
    # If the DB operation failed, log it (but don't re-raise — we still want
    # to return the count of however many succeeded before the failure).
    except sqlite3.Error as e:
        log.error(f"Database error while storing API data: {e}")
    # Return how many rows were inserted.
    return inserted


# ---------------------------------------------------------------------------
# Full workflow: fetch -> store -> JSON output
# ---------------------------------------------------------------------------
# Orchestrator that runs the entire API pipeline end-to-end.
def run_api_workflow(limit: int = 20) -> str:
    """
    End-to-end:
        1. Fetch exercises
        2. Store in DB
        3. Save JSON output
    Returns the path of the JSON output file.
    """
    # Step 1: fetch the data from Wger.
    exercises = fetch_exercises(limit=limit)
    # Step 2: store the data in the database.
    store_exercises_in_db(exercises)
    # Step 3: save the data to a JSON file using the shared save_json helper.
    json_path = save_json(exercises, "exercises_output.json")
    # Return the JSON file path so the caller can show it to the user.
    return json_path