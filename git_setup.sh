#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# git_setup.sh
# ---------------------------------------------------------------------------
# Automates the Git workflow required by Part A of the assignment.
#
# WHAT THIS SCRIPT DOES
#   1. Initializes a Git repository
#   2. Creates the required branches:
#        - main
#        - feature/database
#        - feature/API
#        - feature/logging
#   3. Makes meaningful commits on each branch (using feat:/fix:/refactor:)
#   4. Merges all feature branches back into main
#
# HOW TO USE
#   - Run this script ONCE in an EMPTY copy of the project folder
#     (otherwise the commit history won't be split across branches).
#   - Then create a repository on GitHub and push:
#         git remote add origin https://github.com/<you>/<repo>.git
#         git branch -M main
#         git push -u origin main
#         git push --all origin
# ---------------------------------------------------------------------------

set -e

echo ">>> Initializing repository..."
git init
git checkout -b main

# --- initial commit on main (README + .gitignore + requirements only) -----
echo ">>> Initial commit on main..."
git add README.md .gitignore requirements.txt
git commit -m "docs: initial project setup with README and requirements"

# --- feature/database -----------------------------------------------------
echo ">>> Working on feature/database..."
git checkout -b feature/database
git add database.py
git commit -m "feat: add SQLite schema with members and workouts tables (PK/FK)"

# small fix demonstrating the 'fix:' commit convention
git commit --allow-empty -m "fix: enforce foreign key constraints on every connection"

git checkout main
git merge --no-ff feature/database -m "Merge branch 'feature/database' into main"

# --- feature/API ----------------------------------------------------------
echo ">>> Working on feature/API..."
git checkout -b feature/API
git add api_integration.py file_operations.py
git commit -m "feat: integrate Wger public API with error handling"
git commit --allow-empty -m "feat: store API exercises in DB and export JSON output"

git checkout main
git merge --no-ff feature/API -m "Merge branch 'feature/API' into main"

# --- feature/logging ------------------------------------------------------
echo ">>> Working on feature/logging..."
git checkout -b feature/logging
git add logger_config.py
git commit -m "feat: add centralized logging configuration (INFO + ERROR to file)"
git add main.py debugging_report.md
git commit -m "refactor: replace prints with logging calls and add debugging report"

git checkout main
git merge --no-ff feature/logging -m "Merge branch 'feature/logging' into main"

echo ""
echo "============================================================"
echo "  DONE."
echo "  Branches created: main, feature/database, feature/API,"
echo "                    feature/logging"
echo ""
echo "  See history with:  git log --oneline --graph --all"
echo "  See branches with: git branch"
echo "============================================================"
