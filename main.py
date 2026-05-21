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

# cProfile — Python's built-in profiler. Measures how long functions take.
import cProfile
# pstats — formats and prints profiler results.
import pstats
# io — gives us StringIO, an in-memory text buffer for the profile output.
import io
# sys — for sys.exit() on startup failure.
import sys

# Import the shared logger so every menu action can be logged.
from logger_config import log
# Import all the database functions we need for the menu options.
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
# Import the CSV export and import functions.
from file_operations import (
    export_members_to_csv,
    import_members_from_csv,
)
# Import the API workflow orchestrator.
from api_integration import run_api_workflow


# ---------------------------------------------------------------------------
# Menu actions
# ---------------------------------------------------------------------------
# Menu option 1: print all members.
def action_view_members() -> None:
    # Read all members from the database into a DataFrame.
    df = get_members_df()
    # Header line for visual separation in the terminal.
    print("\n--- All Members ---")
    # If the DataFrame has rows, print it; otherwise show a friendly message.
    # to_string(index=False) prints without the pandas row index column.
    print(df.to_string(index=False) if not df.empty else "(no members)")


# Menu option 2: print all workouts.
def action_view_workouts() -> None:
    # Read all workouts from the database.
    df = get_workouts_df()
    # Header line.
    print("\n--- All Workouts ---")
    # Print the DataFrame, or a placeholder if empty.
    print(df.to_string(index=False) if not df.empty else "(no workouts)")


# Menu option 3: prompt the user for member details and insert them.
def action_add_member() -> None:
    # Wrap input parsing in try/except — int()/float() can raise ValueError.
    try:
        # Read each field via input() and strip whitespace where needed.
        name = input("Name: ").strip()
        # int() will raise ValueError if user types non-numeric.
        age = int(input("Age: "))
        mtype = input("Membership type (Basic/Premium): ").strip()
        join_date = input("Join date (YYYY-MM-DD): ").strip()
        # float() will raise ValueError if user types non-numeric.
        fee = float(input("Monthly fee: "))
        # Call insert_member and capture the new ID.
        new_id = insert_member(name, age, mtype, join_date, fee)
        # Tell the user it worked.
        print(f"Added member with id={new_id}")
    # If the user typed letters where numbers were expected, handle it gracefully.
    except ValueError as e:
        log.error(f"Invalid input while adding member: {e}")
        print("Invalid input — please enter the correct data types.")


# Menu option 4: update a member's monthly fee.
def action_update_fee() -> None:
    # Try to parse the input; handle ValueError if user types non-numeric.
    try:
        # Member ID must be an integer.
        mid = int(input("Member ID: "))
        # Fee must be a number.
        fee = float(input("New monthly fee: "))
        # Call the database function to perform the update.
        update_member_fee(mid, fee)
        # Confirm success to the user.
        print("Fee updated.")
    # Catch invalid input.
    except ValueError as e:
        log.error(f"Invalid input while updating fee: {e}")
        print("Invalid input.")


# Menu option 5: delete a member by ID.
def action_delete_member() -> None:
    # Wrap input parsing in try/except.
    try:
        # Get the member ID as an integer.
        mid = int(input("Member ID to delete: "))
        # Call the database function. Workouts will cascade-delete.
        delete_member(mid)
        # Confirm to user.
        print("Member deleted.")
    # Handle invalid input.
    except ValueError as e:
        log.error(f"Invalid input while deleting member: {e}")
        print("Invalid input.")


# Menu option 6: run both queries and print their results.
def action_run_queries() -> None:
    # Header for Query 1 — AND.
    print("\n--- Query 1: Premium members aged 25+ (AND) ---")
    # Run the AND query and print the resulting DataFrame.
    print(query_premium_adult_members().to_string(index=False))
    # Header for Query 2 — OR.
    print("\n--- Query 2: Long OR high-calorie workouts (OR) ---")
    # Run the OR query and print the resulting DataFrame.
    print(query_high_intensity_workouts().to_string(index=False))


# Menu option 7: export members to CSV.
def action_export_csv() -> None:
    # Call the export function; it returns the path of the file written.
    path = export_members_to_csv()
    # Tell the user where the file was saved.
    print(f"Exported to {path}")


# Menu option 8: import members from the CSV back into a DataFrame.
def action_import_csv() -> None:
    # Read the CSV file and get a DataFrame.
    df = import_members_from_csv()
    # Header line.
    print("\n--- Imported DataFrame ---")
    # Print the imported DataFrame to prove the round trip worked.
    print(df.to_string(index=False))


# Menu option 9: run the full API workflow.
def action_api_workflow() -> None:
    # Call the orchestrator which fetches, stores, and saves JSON.
    path = run_api_workflow(limit=20)
    # Confirm completion and show the JSON file path.
    print(f"API workflow complete. JSON saved to {path}")


# Menu option 10: demonstrate profiling by measuring query performance.
def action_profile_demo() -> None:
    """Profile the query functions to demonstrate Part B (profiling)."""
    # Create a new cProfile profiler object.
    profiler = cProfile.Profile()
    # Start measuring — any function calls from here on are tracked.
    profiler.enable()
    # Run the two queries and the two DataFrame retrievals so there's
    # something to measure.
    query_premium_adult_members()
    query_high_intensity_workouts()
    get_members_df()
    get_workouts_df()
    # Stop measuring.
    profiler.disable()

    # Create an in-memory text buffer to capture the profile report.
    stream = io.StringIO()
    # Wrap the profile data in pstats.Stats and sort by cumulative time.
    stats = pstats.Stats(profiler, stream=stream).sort_stats("cumulative")
    # Print the top 10 slowest functions into the buffer.
    stats.print_stats(10)
    # Header for the report.
    print("\n--- Profiling Report (top 10 by cumulative time) ---")
    # Print the buffer's contents to the terminal.
    print(stream.getvalue())


# ---------------------------------------------------------------------------
# Menu loop
# ---------------------------------------------------------------------------
# Multi-line string holding the menu text shown to the user every loop iteration.
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

# Dispatch dictionary — maps the user's input string to the function to call.
# Cleaner than a long if/elif chain. Works because Python functions are
# first-class objects (you can store them in dicts).
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


# The main loop — runs the application from startup to clean exit.
def main() -> None:
    # Log that the application is starting (goes to gym_app.log).
    log.info("Application starting...")
    # Try to initialise the database. If this fails, the app can't function.
    try:
        # Create the tables (no-op if they already exist).
        create_tables()
        # Seed sample data so the demo has something to show.
        seed_sample_data()
    # Catch any error during startup — broad except is intentional here.
    except Exception as e:
        # Log the failure and exit cleanly with exit code 1.
        log.error(f"Startup failed: {e}")
        print("Could not initialise the database. See log for details.")
        sys.exit(1)

    # Main menu loop — runs forever until the user chooses 0.
    while True:
        # Print the menu.
        print(MENU)
        # Get the user's choice; strip whitespace to be lenient about input.
        choice = input("Choose an option: ").strip()
        # If they chose 0, log the exit and break out of the loop.
        if choice == "0":
            log.info("Application exit requested by user.")
            print("Goodbye.")
            break
        # Look up the action function in the dispatch dict.
        # .get() returns None if the key isn't found — no exception.
        action = ACTIONS.get(choice)
        # If the choice isn't in ACTIONS, tell the user and loop again.
        if not action:
            print("Invalid option, try again.")
            continue
        # Try to run the chosen action.
        try:
            # Call the function. The () actually invokes it.
            action()
        # Catch any error from inside the action so it doesn't crash the menu.
        except Exception as e:
            # Top-level exception handler — nothing crashes the menu
            # Log the error and show it to the user; loop continues.
            log.error(f"Unhandled error in '{choice}': {e}")
            print(f"An error occurred: {e}")


# Standard Python idiom — only run main() if this file is executed directly.
# If another file imports main.py, main() is NOT called automatically.
if __name__ == "__main__":
    main()