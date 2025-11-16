"""Entry point for Splitfool application."""

import argparse
import sqlite3
import sys
from pathlib import Path

from splitfool.config import Config
from splitfool.db.connection import initialize_database
from splitfool.ui.app import SplitfoolApp
from splitfool.utils.db_recovery import check_database_integrity, recover_database


def main() -> int:
    """Main entry point for the application.

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parser = argparse.ArgumentParser(description="Splitfool - Bill Splitting TUI Application")
    parser.add_argument(
        "--db-path",
        type=str,
        help="Path to SQLite database file (default: ./splitfool.db)",
    )
    parser.add_argument(
        "--check-db",
        action="store_true",
        help="Check database integrity and exit",
    )
    parser.add_argument(
        "--recover-db",
        action="store_true",
        help="Attempt to recover corrupted database",
    )

    args = parser.parse_args()

    # Create config
    config = Config(db_path=args.db_path)
    db_path = config.db_path

    # Handle database check/recovery commands
    if args.check_db:
        is_valid, error = check_database_integrity(str(db_path))
        if is_valid:
            print(f"✓ Database is valid: {db_path}")
            return 0
        else:
            print(f"✗ Database has errors: {error}")
            print("  Run with --recover-db to attempt recovery")
            return 1

    if args.recover_db:
        success, message = recover_database(str(db_path))
        print(message)
        return 0 if success else 1

    # Check if database exists and initialize if needed
    if not Path(db_path).exists():
        try:
            initialize_database(str(db_path))
        except Exception as e:
            print(f"Error: Failed to initialize database: {e}", file=sys.stderr)
            print(f"  Database path: {db_path}", file=sys.stderr)
            return 1
    else:
        # Check database integrity on startup
        is_valid, error = check_database_integrity(str(db_path))
        if not is_valid:
            print(f"Error: Database appears to be corrupted: {error}", file=sys.stderr)
            print(f"  Database path: {db_path}", file=sys.stderr)
            print("\nTo recover:", file=sys.stderr)
            print(f"  1. Backup your database: cp {db_path} {db_path}.backup", file=sys.stderr)
            print("  2. Run recovery: splitfool --recover-db", file=sys.stderr)
            print(f"  3. Or manually delete: rm {db_path}", file=sys.stderr)
            return 1

    # Run application with error handling
    try:
        app = SplitfoolApp(config=config)
        app.run()
        return 0
    except sqlite3.DatabaseError as e:
        print(f"Error: Database error occurred: {e}", file=sys.stderr)
        print("  Try running: splitfool --check-db", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        return 0
    except Exception as e:
        print(f"Error: Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
