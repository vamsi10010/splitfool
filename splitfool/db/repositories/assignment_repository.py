"""Assignment repository for database operations."""

import sqlite3
from decimal import Decimal

from splitfool.models.assignment import Assignment


class AssignmentRepository:
    """Repository for Assignment entity database operations."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        """Initialize repository with database connection.

        Args:
            connection: SQLite database connection
        """
        self.conn = connection

    def create(self, assignment: Assignment) -> Assignment:
        """Create a new assignment in the database.

        Args:
            assignment: Assignment to create (id should be None)

        Returns:
            Created assignment with assigned ID
        """
        cursor = self.conn.execute(
            "INSERT INTO assignments (item_id, user_id, fraction) VALUES (?, ?, ?)",
            (assignment.item_id, assignment.user_id, float(assignment.fraction)),
        )
        self.conn.commit()
        return assignment.replace(id=cursor.lastrowid)

    def get_by_item(self, item_id: int) -> list[Assignment]:
        """Get all assignments for an item.

        Args:
            item_id: ID of item

        Returns:
            List of assignments
        """
        cursor = self.conn.execute(
            "SELECT id, item_id, user_id, fraction FROM assignments WHERE item_id = ?",
            (item_id,),
        )
        return [
            Assignment(
                id=row["id"],
                item_id=row["item_id"],
                user_id=row["user_id"],
                fraction=Decimal(str(row["fraction"])),
            )
            for row in cursor.fetchall()
        ]

    def get_by_user(self, user_id: int) -> list[Assignment]:
        """Get all assignments for a user.

        Args:
            user_id: ID of user

        Returns:
            List of assignments
        """
        cursor = self.conn.execute(
            "SELECT id, item_id, user_id, fraction FROM assignments WHERE user_id = ?",
            (user_id,),
        )
        return [
            Assignment(
                id=row["id"],
                item_id=row["item_id"],
                user_id=row["user_id"],
                fraction=Decimal(str(row["fraction"])),
            )
            for row in cursor.fetchall()
        ]

    def delete(self, assignment_id: int) -> None:
        """Delete assignment by ID.

        Args:
            assignment_id: ID of assignment to delete
        """
        self.conn.execute("DELETE FROM assignments WHERE id = ?", (assignment_id,))
        self.conn.commit()

    def validate_fractions_sum(self, item_id: int) -> bool:
        """Validate that fractions for an item sum to 1.0.

        Args:
            item_id: ID of item

        Returns:
            True if fractions sum to 1.0 (within tolerance)
        """
        cursor = self.conn.execute(
            "SELECT SUM(fraction) as total FROM assignments WHERE item_id = ?",
            (item_id,),
        )
        row = cursor.fetchone()
        total = Decimal(str(row["total"])) if row["total"] else Decimal("0")
        return abs(total - Decimal("1.0")) <= Decimal("0.001")
