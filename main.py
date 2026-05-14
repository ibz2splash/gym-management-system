"""
main.py
-------
Entry point for the Gym Management System.

Brings together:
    Part B/C — Database CRUD + DataFrames + logical-operator queries
    Part D   — CSV export/import
    Part E   — Wger API integration
    Part F   — Debugging (3 bugs were fixed; see debugging_report.md)
    Part G   — Logging (configured in logger_config.py)

Also demonstrates:
    - Profiling (cProfile)
    - Top-level exception handling
"""

import cProfile
import pstats
import io
import sys

from logger_config import log
from database import (
    create_tables,
    seed_sample_data,
    get_members_df,
    get_workouts_df,
    insert_member,
    update_member_fee,
    delete_member,
    query_premium_adult_members,
    query_high_intensity_workouts,
)
from file_operations import (
    export_members_to_csv,
    import_members_from_csv,
)
from api_integration import run_api_workflow


# ---------------------------------------------------------------------------
# Menu actions
# ---------------------------------------------------------------------------
def action_view_members() -> None:
    df = get_members_df()
    print("\n--- All Members ---")
    print(df.to_string(index=False) if not df.empty else "(no members)")


def action_view_workouts() -> None:
    df = get_workouts_df()
    print("\n--- All Workouts ---")
    print(df.to_string(index=False) if not df.empty else "(no workouts)")


def action_add_member() -> None:
    try:
        name = input("Name: ").strip()
        age = int(input("Age: "))
        mtype = input("Membership type (Basic/Premium): ").strip()
        join_date = input("Join date (YYYY-MM-DD): ").strip()
        fee = float(input("Monthly fee: "))
        new_id = insert_member(name, age, mtype, join_date, fee)
        print(f"Added member with id={new_id}")
    except ValueError as e:
        log.error(f"Invalid input while adding member: {e}")
        print("Invalid input — please enter the correct data types.")


def action_update_fee() -> None:
    try:
        mid = int(input("Member ID: "))
        fee = float(input("New monthly fee: "))
        update_member_fee(mid, fee)
        print("Fee updated.")
    except ValueError as e:
        log.error(f"Invalid input while updating fee: {e}")
        print("Invalid input.")


def action_delete_member() -> None:
    try:
        mid = int(input("Member ID to delete: "))
        delete_member(mid)
        print("Member deleted.")
    except ValueError as e:
        log.error(f"Invalid input while deleting member: {e}")
        print("Invalid input.")


def action_run_queries() -> None:
    print("\n--- Query 1: Premium members aged 25+ (AND) ---")
    print(query_premium_adult_members().to_string(index=False))
    print("\n--- Query 2: Long OR high-calorie workouts (OR) ---")
    print(query_high_intensity_workouts().to_string(index=False))


def action_export_csv() -> None:
    path = export_members_to_csv()
    print(f"Exported to {path}")


def action_import_csv() -> None:
    df = import_members_from_csv()
    print("\n--- Imported DataFrame ---")
    print(df.to_string(index=False))


def action_api_workflow() -> None:
    path = run_api_workflow(limit=20)
    print(f"API workflow complete. JSON saved to {path}")


def action_profile_demo() -> None:
    """Profile the query functions to demonstrate Part B (profiling)."""
    profiler = cProfile.Profile()
    profiler.enable()
    query_premium_adult_members()
    query_high_intensity_workouts()
    get_members_df()
    get_workouts_df()
    profiler.disable()

    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream).sort_stats("cumulative")
    stats.print_stats(10)
    print("\n--- Profiling Report (top 10 by cumulative time) ---")
    print(stream.getvalue())


# ---------------------------------------------------------------------------
# Menu loop
# ---------------------------------------------------------------------------
MENU = """
=============================================
        GYM MANAGEMENT SYSTEM
=============================================
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
---------------------------------------------
"""

ACTIONS = {
    "1": action_view_members,
    "2": action_view_workouts,
    "3": action_add_member,
    "4": action_update_fee,
    "5": action_delete_member,
    "6": action_run_queries,
    "7": action_export_csv,
    "8": action_import_csv,
    "9": action_api_workflow,
    "10": action_profile_demo,
}


def main() -> None:
    log.info("Application starting...")
    try:
        create_tables()
        seed_sample_data()
    except Exception as e:
        log.error(f"Startup failed: {e}")
        print("Could not initialise the database. See log for details.")
        sys.exit(1)

    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()
        if choice == "0":
            log.info("Application exit requested by user.")
            print("Goodbye.")
            break
        action = ACTIONS.get(choice)
        if not action:
            print("Invalid option, try again.")
            continue
        try:
            action()
        except Exception as e:
            # Top-level exception handler — nothing crashes the menu
            log.error(f"Unhandled error in '{choice}': {e}")
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
