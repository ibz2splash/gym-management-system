# Debugging Report — Gym Management System

This document satisfies **Part F** of the assignment.
Three intentional bugs were injected during development, detected through testing,
fixed, and documented below. The original `print()` debugging statements were then
replaced with proper `logging` calls (see Part G).

---

## Bug #1 — Forgotten `commit()` after INSERT

### Buggy code (initial version of `database.py`)
```python
def insert_member(name, age, ...):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("INSERT INTO members ... VALUES (?, ?, ...);", (...))
    # MISSING: conn.commit()
    conn.close()
```

### Symptom
After calling `insert_member()`, querying the database returned **zero rows**, even
though the script reported success.

### Detection
We added a debug `print()` after the insert:
```python
print("[DEBUG] cursor.lastrowid =", cur.lastrowid)
```
This printed a valid id, so the INSERT was reaching the cursor — but the row was
never persisted, indicating the transaction was never committed.

### Fix
Added `conn.commit()` before closing the connection, and refactored to use a
context manager (`with get_connection() as conn`) so commits are handled cleanly.

### Logging replacement
```python
log.info(f"Inserted member id={new_id} name='{name}'")
```

---

## Bug #2 — Foreign-key constraint not enforced

### Buggy code
```python
def get_connection():
    return sqlite3.connect(DB_NAME)
```

### Symptom
We could insert a workout with `member_id = 999` (a non-existent member) and
SQLite happily accepted it — orphan rows polluted the workouts table.

### Detection
Print-debugging exposed the issue:
```python
print("[DEBUG] FK pragma =",
      conn.execute("PRAGMA foreign_keys;").fetchone())
# Output: (0,)   <-- foreign keys are OFF by default in SQLite
```

### Fix
SQLite disables foreign-key enforcement by default on every connection. We now
enable it explicitly inside `get_connection()`:
```python
conn.execute("PRAGMA foreign_keys = ON;")
```

### Logging replacement
Errors raised by FK violations are now caught and logged:
```python
log.error(f"Failed to insert workout for member {member_id}: {e}")
```

---

## Bug #3 — CSV import crashed on missing file

### Buggy code
```python
def import_members_from_csv(filename="members_export.csv"):
    df = pd.read_csv(filename)   # crashes if file doesn't exist
    return df
```

### Symptom
The whole program crashed with an ugly `FileNotFoundError` traceback whenever a
user clicked "Import CSV" before exporting. The menu loop also exited.

### Detection
Adding a `print("[DEBUG] looking for file:", filename)` showed the path was
correct, but the file simply wasn't there yet on a fresh run.

### Fix
Two improvements:
1. Wrap the read in a `try/except` block that handles both `FileNotFoundError`
   and `pandas.errors.EmptyDataError`.
2. Compose the path using `os.path.join(EXPORT_DIR, filename)` so the import
   looks in the right folder.
3. In `main.py`, the menu loop has a top-level `try/except` so a single failure
   never kills the whole app.

### Logging replacement
```python
log.error(f"CSV file not found: {path}")
```

---

## Summary

| # | Bug                                  | Type          | Fix                                          |
|---|--------------------------------------|---------------|----------------------------------------------|
| 1 | Missing `conn.commit()` after INSERT | Data loss     | Use context manager + explicit commit         |
| 2 | Foreign keys not enforced            | Data integrity| `PRAGMA foreign_keys = ON;` on every connect |
| 3 | Crash on missing CSV file            | Robustness    | `try/except FileNotFoundError`                |

All temporary `print()` statements were replaced with `logging` calls, and the
log output is persisted in `logs/gym_app.log`.
