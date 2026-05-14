"""
database.py
-----------
SQLite database module for the Gym Management System.

Covers:
    - Part B: Design SQLite database (two tables with PK/FK relationship)
    - Part C: Insert / Update / Delete / Retrieve into DataFrames + two queries
              using logical operators (AND / OR).
"""

import sqlite3
import pandas as pd
from logger_config import log

DB_NAME = "gym.db"


# ---------------------------------------------------------------------------
# Part B — Schema creation
# ---------------------------------------------------------------------------
def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection with foreign keys enforced."""
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except sqlite3.Error as e:
        log.error(f"Failed to connect to database: {e}")
        raise


def create_tables() -> None:
    """
    Create the two tables.

    members  : primary key = member_id
    workouts : primary key = workout_id, foreign key member_id -> members
    """
    log.info("Creating tables (if they do not exist)...")
    try:
        with get_connection() as conn:
            cur = conn.cursor()

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
            conn.commit()
        log.info("Tables created successfully.")
    except sqlite3.Error as e:
        log.error(f"Error creating tables: {e}")
        raise


# ---------------------------------------------------------------------------
# Part C — Insert / Update / Delete
# ---------------------------------------------------------------------------
def insert_member(name: str, age: int, membership_type: str,
                  join_date: str, monthly_fee: float) -> int:
    """Insert a new member and return its member_id."""
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """INSERT INTO members
                   (name, age, membership_type, join_date, monthly_fee)
                   VALUES (?, ?, ?, ?, ?);""",
                (name, age, membership_type, join_date, monthly_fee),
            )
            conn.commit()
            new_id = cur.lastrowid
        log.info(f"Inserted member id={new_id} name='{name}'")
        return new_id
    except sqlite3.Error as e:
        log.error(f"Failed to insert member '{name}': {e}")
        raise


def insert_workout(member_id: int, exercise_name: str, muscle_group: str,
                   workout_date: str, duration_minutes: int,
                   calories_burned: int) -> int:
    """Insert a new workout linked to an existing member."""
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """INSERT INTO workouts
                   (member_id, exercise_name, muscle_group, workout_date,
                    duration_minutes, calories_burned)
                   VALUES (?, ?, ?, ?, ?, ?);""",
                (member_id, exercise_name, muscle_group, workout_date,
                 duration_minutes, calories_burned),
            )
            conn.commit()
            new_id = cur.lastrowid
        log.info(f"Inserted workout id={new_id} for member_id={member_id}")
        return new_id
    except sqlite3.Error as e:
        log.error(f"Failed to insert workout for member {member_id}: {e}")
        raise


def update_member_fee(member_id: int, new_fee: float) -> None:
    """Update the monthly_fee of a given member."""
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE members SET monthly_fee = ? WHERE member_id = ?;",
                (new_fee, member_id),
            )
            conn.commit()
        log.info(f"Updated member_id={member_id} monthly_fee={new_fee}")
    except sqlite3.Error as e:
        log.error(f"Failed to update member {member_id}: {e}")
        raise


def delete_member(member_id: int) -> None:
    """Delete a member (workouts cascade)."""
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM members WHERE member_id = ?;", (member_id,))
            conn.commit()
        log.info(f"Deleted member_id={member_id}")
    except sqlite3.Error as e:
        log.error(f"Failed to delete member {member_id}: {e}")
        raise


# ---------------------------------------------------------------------------
# Part C — Retrieve records into DataFrames
# ---------------------------------------------------------------------------
def get_members_df() -> pd.DataFrame:
    """Return all members as a DataFrame."""
    try:
        with get_connection() as conn:
            df = pd.read_sql_query("SELECT * FROM members;", conn)
        log.info(f"Retrieved {len(df)} members into DataFrame.")
        return df
    except Exception as e:
        log.error(f"Failed to retrieve members: {e}")
        raise


def get_workouts_df() -> pd.DataFrame:
    """Return all workouts as a DataFrame."""
    try:
        with get_connection() as conn:
            df = pd.read_sql_query("SELECT * FROM workouts;", conn)
        log.info(f"Retrieved {len(df)} workouts into DataFrame.")
        return df
    except Exception as e:
        log.error(f"Failed to retrieve workouts: {e}")
        raise


# ---------------------------------------------------------------------------
# Part C — Two queries using logical operators
# ---------------------------------------------------------------------------
def query_premium_adult_members() -> pd.DataFrame:
    """
    Query 1 — uses AND.
    Premium members who are also 25 years or older.
    """
    sql = """
        SELECT member_id, name, age, membership_type, monthly_fee
        FROM members
        WHERE membership_type = 'Premium' AND age >= 25;
    """
    with get_connection() as conn:
        df = pd.read_sql_query(sql, conn)
    log.info(f"Query 1 (AND) returned {len(df)} rows.")
    return df


def query_high_intensity_workouts() -> pd.DataFrame:
    """
    Query 2 — uses OR.
    Workouts that are either long (> 45 min) or burn many calories (> 400).
    """
    sql = """
        SELECT workout_id, member_id, exercise_name, duration_minutes,
               calories_burned
        FROM workouts
        WHERE duration_minutes > 45 OR calories_burned > 400;
    """
    with get_connection() as conn:
        df = pd.read_sql_query(sql, conn)
    log.info(f"Query 2 (OR) returned {len(df)} rows.")
    return df


# ---------------------------------------------------------------------------
# Seed sample data so the program is demo-ready
# ---------------------------------------------------------------------------
def seed_sample_data() -> None:
    """Insert a small set of sample rows if the tables are empty."""
    with get_connection() as conn:
        count = conn.execute("SELECT COUNT(*) FROM members;").fetchone()[0]
    if count > 0:
        log.info("Sample data already present, skipping seeding.")
        return

    log.info("Seeding sample data...")
    m1 = insert_member("Ibrahim Baqer",   24, "Premium", "2025-09-01", 45.0)
    m2 = insert_member("Sara Al-Lawati",    31, "Basic",   "2025-11-15", 25.0)
    m3 = insert_member("Khalid Al-Habsi",   28, "Premium", "2026-01-10", 45.0)
    m4 = insert_member("Aisha Al-Riyami",   22, "Basic",   "2026-02-20", 25.0)

    insert_workout(m1, "Deadlift",     "Back",      "2026-05-10", 60, 480)
    insert_workout(m1, "Barbell Curl", "Biceps",    "2026-05-10", 30, 180)
    insert_workout(m2, "Bench Press",  "Chest",     "2026-05-11", 45, 350)
    insert_workout(m3, "Squat",        "Legs",      "2026-05-12", 50, 520)
    insert_workout(m3, "Plank",        "Abs",       "2026-05-12", 15, 90)
    insert_workout(m4, "Shoulder Press","Shoulders","2026-05-13", 40, 300)
    log.info("Sample data seeded.")
