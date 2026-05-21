"""
database.py
-----------
SQLite database module for the Gym Management System.
 
Covers:
    - Part B: Design SQLite database (two tables with PK/FK relationship)
    - Part C: Insert / Update / Delete / Retrieve into DataFrames + two queries
              using logical operators (AND / OR).
"""
 
# Python's built-in SQLite library — no external install required.
import sqlite3
# pandas for DataFrames (used by the read functions).
import pandas as pd
# Import the shared logger from logger_config so every action is logged.
from logger_config import log
 
# The database filename. Defined once as a constant so it appears in one place.
DB_NAME = "gym.db"
 
 
# ---------------------------------------------------------------------------
# Part B — Schema creation
# ---------------------------------------------------------------------------
# Open a connection to the SQLite database and turn on foreign-key enforcement.
def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection with foreign keys enforced."""
    # Try to open the connection; log and re-raise if it fails.
    try:
        # sqlite3.connect opens (or creates if it doesn't exist) the .db file.
        conn = sqlite3.connect(DB_NAME)
        # PRAGMA foreign_keys = ON; turns on FK enforcement.
        # SQLite has this OFF by default — without this line, FOREIGN KEY
        # clauses in CREATE TABLE are decorative only.
        conn.execute("PRAGMA foreign_keys = ON;")
        # Return the live connection to the caller.
        return conn
    # If anything went wrong while connecting, log the error...
    except sqlite3.Error as e:
        log.error(f"Failed to connect to database: {e}")
        # ...and re-raise it so the caller knows the failure happened.
        raise
 
 
# Create both tables if they don't already exist.
def create_tables() -> None:
    """
    Create the two tables.
 
    members  : primary key = member_id
    workouts : primary key = workout_id, foreign key member_id -> members
    """
    # Log that we're about to attempt table creation.
    log.info("Creating tables (if they do not exist)...")
    # Wrap in try/except so errors are captured and logged.
    try:
        # Use the connection as a context manager so it closes cleanly.
        with get_connection() as conn:
            # Get a cursor — the object that executes SQL statements.
            cur = conn.cursor()
 
            # Create the parent 'members' table if it doesn't exist.
            # member_id is the primary key, auto-incremented by SQLite.
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS members (
                    member_id       INTEGER PRIMARY KEY AUTOINCREMENT,
                    name            TEXT    NOT NULL,
                    age             INTEGER NOT NULL,
                    membership_type TEXT    NOT NULL,
                    join_date       TEXT    NOT NULL,
                    monthly_fee     REAL    NOT NULL
                );
                """
            )
 
            # Create the child 'workouts' table if it doesn't exist.
            # workout_id is the primary key. member_id is the foreign key
            # linking each workout to a member. ON DELETE CASCADE means
            # deleting a member automatically deletes their workouts.
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS workouts (
                    workout_id       INTEGER PRIMARY KEY AUTOINCREMENT,
                    member_id        INTEGER NOT NULL,
                    exercise_name    TEXT    NOT NULL,
                    muscle_group     TEXT    NOT NULL,
                    workout_date     TEXT    NOT NULL,
                    duration_minutes INTEGER NOT NULL,
                    calories_burned  INTEGER NOT NULL,
                    FOREIGN KEY (member_id) REFERENCES members(member_id)
                        ON DELETE CASCADE
                );
                """
            )
            # Persist the CREATE TABLE changes to disk.
            conn.commit()
        # Log success.
        log.info("Tables created successfully.")
    # If something went wrong creating tables, log and re-raise.
    except sqlite3.Error as e:
        log.error(f"Error creating tables: {e}")
        raise
 
 
# ---------------------------------------------------------------------------
# Part C — Insert / Update / Delete
# ---------------------------------------------------------------------------
# Insert a new member record. Returns the auto-generated member_id.
def insert_member(name: str, age: int, membership_type: str,
                  join_date: str, monthly_fee: float) -> int:
    """Insert a new member and return its member_id."""
    # Catch any SQLite errors so we can log them properly.
    try:
        # Open connection via context manager.
        with get_connection() as conn:
            # Cursor for executing SQL.
            cur = conn.cursor()
            # Parameterised INSERT — the ? placeholders are replaced by the
            # tuple values. This prevents SQL injection by treating input
            # as data, not as code.
            cur.execute(
                """INSERT INTO members
                   (name, age, membership_type, join_date, monthly_fee)
                   VALUES (?, ?, ?, ?, ?);""",
                (name, age, membership_type, join_date, monthly_fee),
            )
            # Commit persists the insert — without this, the change is lost.
            conn.commit()
            # lastrowid is the auto-incremented ID SQLite just assigned.
            new_id = cur.lastrowid
        # Log the successful insert with the new ID.
        log.info(f"Inserted member id={new_id} name='{name}'")
        # Return the new ID so the caller can use it.
        return new_id
    # If SQLite raised an error, log it and re-raise.
    except sqlite3.Error as e:
        log.error(f"Failed to insert member '{name}': {e}")
        raise
 
 
# Insert a new workout record linked to an existing member via FK.
def insert_workout(member_id: int, exercise_name: str, muscle_group: str,
                   workout_date: str, duration_minutes: int,
                   calories_burned: int) -> int:
    """Insert a new workout linked to an existing member."""
    # Try/except wraps the entire DB operation.
    try:
        # Context-managed connection.
        with get_connection() as conn:
            # Cursor for SQL execution.
            cur = conn.cursor()
            # Parameterised INSERT for the workouts table.
            # member_id must exist in members or the FK constraint will fail.
            cur.execute(
                """INSERT INTO workouts
                   (member_id, exercise_name, muscle_group, workout_date,
                    duration_minutes, calories_burned)
                   VALUES (?, ?, ?, ?, ?, ?);""",
                (member_id, exercise_name, muscle_group, workout_date,
                 duration_minutes, calories_burned),
            )
            # Persist the insert.
            conn.commit()
            # Get the new workout's auto-generated ID.
            new_id = cur.lastrowid
        # Log the successful insert.
        log.info(f"Inserted workout id={new_id} for member_id={member_id}")
        # Return the new workout ID.
        return new_id
    # Catch and log any SQLite-specific errors.
    except sqlite3.Error as e:
        log.error(f"Failed to insert workout for member {member_id}: {e}")
        raise
 
 
# Change the monthly_fee of a member identified by member_id.
def update_member_fee(member_id: int, new_fee: float) -> None:
    """Update the monthly_fee of a given member."""
    # Wrap the operation in try/except.
    try:
        # Open the connection.
        with get_connection() as conn:
            # Get a cursor.
            cur = conn.cursor()
            # UPDATE statement with parameterised values.
            # WHERE clause is essential — without it every row would be updated.
            cur.execute(
                "UPDATE members SET monthly_fee = ? WHERE member_id = ?;",
                (new_fee, member_id),
            )
            # Persist the change to disk.
            conn.commit()
        # Log the successful update.
        log.info(f"Updated member_id={member_id} monthly_fee={new_fee}")
    # Catch SQLite errors and re-raise so the caller knows.
    except sqlite3.Error as e:
        log.error(f"Failed to update member {member_id}: {e}")
        raise
 
 
# Delete a member by ID. Workouts cascade-delete automatically.
def delete_member(member_id: int) -> None:
    """Delete a member (workouts cascade)."""
    # Try/except wrapper.
    try:
        # Open connection.
        with get_connection() as conn:
            # Cursor for executing SQL.
            cur = conn.cursor()
            # DELETE with parameterised member_id. The single-element tuple
            # (member_id,) is required — a bare value wouldn't be iterable.
            cur.execute("DELETE FROM members WHERE member_id = ?;", (member_id,))
            # Persist the delete.
            conn.commit()
        # Log the deletion.
        log.info(f"Deleted member_id={member_id}")
    # Catch SQLite errors.
    except sqlite3.Error as e:
        log.error(f"Failed to delete member {member_id}: {e}")
        raise
 
 
# ---------------------------------------------------------------------------
# Part C — Retrieve records into DataFrames
# ---------------------------------------------------------------------------
# Read all rows from the members table into a pandas DataFrame.
def get_members_df() -> pd.DataFrame:
    """Return all members as a DataFrame."""
    # Try the query; on failure, log and re-raise.
    try:
        # Open the connection.
        with get_connection() as conn:
            # pd.read_sql_query runs the SQL and returns a DataFrame with
            # columns named after the SQL columns. One line, big payoff.
            df = pd.read_sql_query("SELECT * FROM members;", conn)
        # Log how many rows came back.
        log.info(f"Retrieved {len(df)} members into DataFrame.")
        # Return the DataFrame.
        return df
    # Catch any error (broader than just sqlite3.Error because pandas may raise).
    except Exception as e:
        log.error(f"Failed to retrieve members: {e}")
        raise
 
 
# Read all rows from the workouts table into a pandas DataFrame.
def get_workouts_df() -> pd.DataFrame:
    """Return all workouts as a DataFrame."""
    # Try the query.
    try:
        # Open the connection.
        with get_connection() as conn:
            # Same pattern as get_members_df, just a different table.
            df = pd.read_sql_query("SELECT * FROM workouts;", conn)
        # Log the row count.
        log.info(f"Retrieved {len(df)} workouts into DataFrame.")
        # Return the DataFrame.
        return df
    # Catch any error and log it.
    except Exception as e:
        log.error(f"Failed to retrieve workouts: {e}")
        raise
 
 
# ---------------------------------------------------------------------------
# Part C — Two queries using logical operators
# ---------------------------------------------------------------------------
# Query 1: demonstrates the AND logical operator.
def query_premium_adult_members() -> pd.DataFrame:
    """
    Query 1 — uses AND.
    Premium members who are also 25 years or older.
    """
    # SQL with WHERE ... AND ... — both conditions must be true.
    sql = """
        SELECT member_id, name, age, membership_type, monthly_fee
        FROM members
        WHERE membership_type = 'Premium' AND age >= 25;
    """
    # Open the connection and run the query into a DataFrame.
    with get_connection() as conn:
        df = pd.read_sql_query(sql, conn)
    # Log the number of matching rows.
    log.info(f"Query 1 (AND) returned {len(df)} rows.")
    # Return the result.
    return df
 
 
# Query 2: demonstrates the OR logical operator.
def query_high_intensity_workouts() -> pd.DataFrame:
    """
    Query 2 — uses OR.
    Workouts that are either long (> 45 min) or burn many calories (> 400).
    """
    # SQL with WHERE ... OR ... — either condition is enough.
    sql = """
        SELECT workout_id, member_id, exercise_name, duration_minutes,
               calories_burned
        FROM workouts
        WHERE duration_minutes > 45 OR calories_burned > 400;
    """
    # Open the connection and run the query into a DataFrame.
    with get_connection() as conn:
        df = pd.read_sql_query(sql, conn)
    # Log the number of matching rows.
    log.info(f"Query 2 (OR) returned {len(df)} rows.")
    # Return the result.
    return df
 
 
# ---------------------------------------------------------------------------
# Seed sample data so the program is demo-ready
# ---------------------------------------------------------------------------
# Insert a default set of members and workouts so the demo has data to show.
def seed_sample_data() -> None:
    """Insert a small set of sample rows if the tables are empty."""
    # Open the connection just to check how many members exist.
    with get_connection() as conn:
        # SELECT COUNT(*) returns one row with one column: the row count.
        count = conn.execute("SELECT COUNT(*) FROM members;").fetchone()[0]
    # If there's already data, don't re-seed (avoids duplicates).
    if count > 0:
        log.info("Sample data already present, skipping seeding.")
        return
 
    # Otherwise log that we're about to seed.
    log.info("Seeding sample data...")
    # Insert four sample members and capture their auto-generated IDs.
    m1 = insert_member("Ibrahim Baqer",   24, "Premium", "2025-09-01", 45.0)
    m2 = insert_member("Sara Al-Lawati",    31, "Basic",   "2025-11-15", 25.0)
    m3 = insert_member("Khalid Al-Habsi",   28, "Premium", "2026-01-10", 45.0)
    m4 = insert_member("Aisha Al-Riyami",   22, "Basic",   "2026-02-20", 25.0)
 
    # Insert six sample workouts, each linked to a member via the FK.
    insert_workout(m1, "Deadlift",     "Back",      "2026-05-10", 60, 480)
    insert_workout(m1, "Barbell Curl", "Biceps",    "2026-05-10", 30, 180)
    insert_workout(m2, "Bench Press",  "Chest",     "2026-05-11", 45, 350)
    insert_workout(m3, "Squat",        "Legs",      "2026-05-12", 50, 520)
    insert_workout(m3, "Plank",        "Abs",       "2026-05-12", 15, 90)
    insert_workout(m4, "Shoulder Press","Shoulders","2026-05-13", 40, 300)
    # Log completion.
    log.info("Sample data seeded.")
 