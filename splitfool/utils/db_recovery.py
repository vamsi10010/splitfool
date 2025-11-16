"""Database corruption recovery utilities."""

import sqlite3
from pathlib import Path


def check_database_integrity(db_path: str) -> tuple[bool, str | None]:
    """Check database integrity.

    Args:
        db_path: Path to database file

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.execute("PRAGMA integrity_check")
        result = cursor.fetchone()[0]
        conn.close()

        if result == "ok":
            return True, None
        else:
            return False, f"Database integrity check failed: {result}"
    except sqlite3.DatabaseError as e:
        return False, f"Database error: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def backup_database(db_path: str) -> str | None:
    """Create backup of database.

    Args:
        db_path: Path to database file

    Returns:
        Path to backup file, or None if backup failed
    """
    try:
        source = Path(db_path)
        if not source.exists():
            return None

        backup_path = source.parent / f"{source.stem}_backup_{source.suffix}"

        import shutil
        shutil.copy2(source, backup_path)
        return str(backup_path)
    except Exception:
        return None


def recover_database(db_path: str) -> tuple[bool, str]:
    """Attempt to recover corrupted database.

    Args:
        db_path: Path to database file

    Returns:
        Tuple of (success, message)
    """
    from splitfool.db.connection import initialize_database

    # Check current database
    is_valid, error = check_database_integrity(db_path)
    if is_valid:
        return True, "Database is valid, no recovery needed"

    # Create backup
    backup_path = backup_database(db_path)
    if backup_path:
        backup_msg = f"Backup created at: {backup_path}"
    else:
        backup_msg = "Failed to create backup"

    try:
        # Remove corrupted database
        Path(db_path).unlink()

        # Initialize fresh database
        initialize_database(db_path)

        return True, f"Database recreated successfully. {backup_msg}"
    except Exception as e:
        return False, f"Recovery failed: {str(e)}. {backup_msg}"
