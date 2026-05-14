# Gym Management System — Python Mini-Application

**Module:** Advanced Programming (DTSC2207)
**Semester:** 4 — Spring 2025/2026
**Project type:** Group Project (max 2 students)

---

## 1. Project Description

A Python mini-application that simulates a small **Gym Management System**.
It tracks **members** and their **workouts**, integrates with the public
[Wger Workout Manager API](https://wger.de/api/v2/) to fetch real exercise
data, and demonstrates the full toolkit covered in the module:

| Requirement | Where it's covered |
|---|---|
| **SQLite database** with PK/FK | `database.py` — `members` + `workouts` tables |
| **CSV** import/export | `file_operations.py` |
| **JSON** output | `exports/exercises_output.json` |
| **API** integration | `api_integration.py` (Wger API) |
| **Pandas DataFrames** | every `get_*_df()` and query function |
| **Debugging** | see `debugging_report.md` |
| **Logging** (INFO + ERROR, to file) | `logger_config.py` → `logs/gym_app.log` |
| **Profiling** | `action_profile_demo()` in `main.py` |
| **Exception handling** | every module + top-level try/except in main loop |
| **Git / GitHub** | repository link below |

---

## 2. File Structure

```
gym_management_system/
├── main.py                    # Entry point — interactive menu
├── database.py                # SQLite schema + CRUD + queries (Parts B, C)
├── file_operations.py         # CSV export/import + JSON saver (Part D)
├── api_integration.py         # Wger API integration (Part E)
├── logger_config.py           # Logging configuration (Part G)
├── gym.db                     # SQLite database (auto-created)
├── exports/
│   ├── members_export.csv     # CSV output
│   └── exercises_output.json  # API → JSON output
├── logs/
│   └── gym_app.log            # Log file
├── debugging_report.md        # Part F — bug analysis
├── requirements.txt
└── README.md
```

---

## 3. How to Run

### Prerequisites
- Python 3.10 or higher
- `pip` package manager

### Setup

```bash
# 1. Clone the repository
git clone <your-github-repo-url>
cd gym_management_system

# 2. (Optional) create a virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python main.py
```

### Menu options

```
 1. View all members
 2. View all workouts
 3. Add a member
 4. Update member's monthly fee
 5. Delete a member
 6. Run the two queries (AND / OR)
 7. Export members to CSV
 8. Import members from CSV
 9. Fetch exercises from Wger API
10. Run profiling demo
 0. Exit
```

On first run, the program seeds four sample members and six sample workouts so
the menu options work immediately.

---

## 4. Database Schema

### Table 1 — `members`
| Column          | Type    | Constraints              |
|-----------------|---------|--------------------------|
| member_id       | INTEGER | **PRIMARY KEY**, autoinc |
| name            | TEXT    | NOT NULL                 |
| age             | INTEGER | NOT NULL                 |
| membership_type | TEXT    | NOT NULL                 |
| join_date       | TEXT    | NOT NULL                 |
| monthly_fee     | REAL    | NOT NULL                 |

### Table 2 — `workouts`
| Column           | Type    | Constraints                                       |
|------------------|---------|---------------------------------------------------|
| workout_id       | INTEGER | **PRIMARY KEY**, autoinc                          |
| member_id        | INTEGER | **FOREIGN KEY** → members(member_id), ON DELETE CASCADE |
| exercise_name    | TEXT    | NOT NULL                                          |
| muscle_group     | TEXT    | NOT NULL                                          |
| workout_date     | TEXT    | NOT NULL                                          |
| duration_minutes | INTEGER | NOT NULL                                          |
| calories_burned  | INTEGER | NOT NULL                                          |

---

## 5. The Two Logical-Operator Queries (Part C)

**Query 1 — uses `AND`:** Premium members aged 25 or older.
```sql
SELECT member_id, name, age, membership_type, monthly_fee
FROM members
WHERE membership_type = 'Premium' AND age >= 25;
```

**Query 2 — uses `OR`:** Workouts that are long *or* high-calorie.
```sql
SELECT workout_id, member_id, exercise_name, duration_minutes, calories_burned
FROM workouts
WHERE duration_minutes > 45 OR calories_burned > 400;
```

---

## 6. Git Workflow (Part A)

The repository follows the workflow required by the assignment:

```bash
# Initialize
git init
git remote add origin <your-github-url>

# Branches created
main
feature/database
feature/API
feature/logging

# Example commit messages (use these conventions)
git commit -m "feat: add members and workouts tables with PK/FK"
git commit -m "feat: implement insert/update/delete operations"
git commit -m "feat: integrate Wger API with error handling"
git commit -m "fix: enforce foreign key constraints on every connection"
git commit -m "refactor: replace prints with logging calls"
git commit -m "feat: add CSV export/import and JSON output"
git commit -m "docs: add README and debugging report"

# Merge feature branches into main via Pull Requests on GitHub
```

> **Insert your Git screenshots here** (branches view, commit history,
> merged pull requests).

**GitHub repository:** `<paste your repo URL here>`

---

## 7. Team Management

| Team Member | Role | Tasks |
|---|---|---|
| Member 1 | Database & File Handling | `database.py`, `file_operations.py`, CSV/JSON, debugging report |
| Member 2 | API, Logging & Integration | `api_integration.py`, `logger_config.py`, `main.py`, profiling, README |

---

## 8. References

- Python Software Foundation. (2025). *sqlite3 — DB-API 2.0 interface for SQLite databases.* Python 3 documentation.
- Pandas Development Team. (2025). *pandas: powerful data analysis toolkit.*
- Reitz, K. (2025). *Requests: HTTP for Humans.*
- Wger Project. (2026). *Wger Workout Manager API v2 documentation.*
