"""Settlement repository for database operations."""

import sqlite3
from datetime import datetime

from splitfool.models.settlement import Settlement


class SettlementRepository:
    """Repository for Settlement entity database operations."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        """Initialize repository with database connection.

        Args:
            connection: SQLite database connection
        """
        self.conn = connection

    def create(self, settlement: Settlement) -> Settlement:
        """Create a new settlement in the database.

        Args:
            settlement: Settlement to create (id should be None)

        Returns:
            Created settlement with assigned ID
        """
        cursor = self.conn.execute(
            "INSERT INTO settlements (settled_at, note) VALUES (?, ?)",
            (settlement.settled_at, settlement.note),
        )
        self.conn.commit()
        return settlement.replace(id=cursor.lastrowid)

    def get_latest(self) -> Settlement | None:
        """Get the most recent settlement.

        Returns:
            Most recent settlement or None if no settlements exist
        """
        cursor = self.conn.execute(
            "SELECT id, settled_at, note FROM settlements "
            "ORDER BY settled_at DESC LIMIT 1"
        )
        row = cursor.fetchone()
        if not row:
            return None
        return Settlement(
            id=row["id"],
            settled_at=datetime.fromisoformat(row["settled_at"]),
            note=row["note"] or "",
        )

    def get_all(self) -> list[Settlement]:
        """Get all settlements ordered by date (newest first).

        Returns:
            List of all settlements
        """
        cursor = self.conn.execute(
            "SELECT id, settled_at, note FROM settlements ORDER BY settled_at DESC"
        )
        return [
            Settlement(
                id=row["id"],
                settled_at=datetime.fromisoformat(row["settled_at"]),
                note=row["note"] or "",
            )
            for row in cursor.fetchall()
        ]
