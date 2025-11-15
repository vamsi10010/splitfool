"""Bill repository for database operations."""

import sqlite3
from datetime import datetime
from decimal import Decimal

from splitfool.models.bill import Bill
from splitfool.utils.errors import BillNotFoundError


class BillRepository:
    """Repository for Bill entity database operations."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        """Initialize repository with database connection.

        Args:
            connection: SQLite database connection
        """
        self.conn = connection

    def create(self, bill: Bill) -> Bill:
        """Create a new bill in the database.

        Args:
            bill: Bill to create (id should be None)

        Returns:
            Created bill with assigned ID
        """
        cursor = self.conn.execute(
            "INSERT INTO bills (payer_id, description, tax, created_at) VALUES (?, ?, ?, ?)",
            (bill.payer_id, bill.description, float(bill.tax), bill.created_at),
        )
        self.conn.commit()
        return bill.replace(id=cursor.lastrowid)

    def get(self, bill_id: int) -> Bill:
        """Get bill by ID.

        Args:
            bill_id: ID of bill to retrieve

        Returns:
            Bill instance

        Raises:
            BillNotFoundError: If bill not found
        """
        cursor = self.conn.execute(
            "SELECT id, payer_id, description, tax, created_at FROM bills WHERE id = ?",
            (bill_id,),
        )
        row = cursor.fetchone()
        if not row:
            raise BillNotFoundError(
                f"Bill with ID {bill_id} not found",
                code="BILL_001",
            )
        return Bill(
            id=row["id"],
            payer_id=row["payer_id"],
            description=row["description"],
            tax=Decimal(str(row["tax"])),
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def get_all(self, limit: int = 100, offset: int = 0) -> list[Bill]:
        """Get all bills with pagination.

        Args:
            limit: Maximum number of bills to return
            offset: Number of bills to skip

        Returns:
            List of bills ordered by creation date (newest first)
        """
        cursor = self.conn.execute(
            "SELECT id, payer_id, description, tax, created_at FROM bills "
            "ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        )
        return [
            Bill(
                id=row["id"],
                payer_id=row["payer_id"],
                description=row["description"],
                tax=Decimal(str(row["tax"])),
                created_at=datetime.fromisoformat(row["created_at"]),
            )
            for row in cursor.fetchall()
        ]

    def get_by_user(self, user_id: int) -> list[Bill]:
        """Get all bills where user is the payer.

        Args:
            user_id: ID of user

        Returns:
            List of bills
        """
        cursor = self.conn.execute(
            "SELECT id, payer_id, description, tax, created_at FROM bills "
            "WHERE payer_id = ? ORDER BY created_at DESC",
            (user_id,),
        )
        return [
            Bill(
                id=row["id"],
                payer_id=row["payer_id"],
                description=row["description"],
                tax=Decimal(str(row["tax"])),
                created_at=datetime.fromisoformat(row["created_at"]),
            )
            for row in cursor.fetchall()
        ]

    def get_since_date(self, since: datetime) -> list[Bill]:
        """Get all bills created since a specific date.

        Args:
            since: DateTime threshold

        Returns:
            List of bills created after the threshold
        """
        cursor = self.conn.execute(
            "SELECT id, payer_id, description, tax, created_at FROM bills "
            "WHERE created_at > ? ORDER BY created_at DESC",
            (since,),
        )
        return [
            Bill(
                id=row["id"],
                payer_id=row["payer_id"],
                description=row["description"],
                tax=Decimal(str(row["tax"])),
                created_at=datetime.fromisoformat(row["created_at"]),
            )
            for row in cursor.fetchall()
        ]
