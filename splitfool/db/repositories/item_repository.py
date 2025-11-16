"""Item repository for database operations."""

import sqlite3
from decimal import Decimal

from splitfool.models.item import Item


class ItemRepository:
    """Repository for Item entity database operations."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        """Initialize repository with database connection.

        Args:
            connection: SQLite database connection
        """
        self.conn = connection

    def create(self, item: Item) -> Item:
        """Create a new item in the database.

        Args:
            item: Item to create (id should be None)

        Returns:
            Created item with assigned ID
        """
        cursor = self.conn.execute(
            "INSERT INTO items (bill_id, description, cost) VALUES (?, ?, ?)",
            (item.bill_id, item.description, float(item.cost)),
        )
        self.conn.commit()
        return item.replace(id=cursor.lastrowid)

    def get_by_bill(self, bill_id: int) -> list[Item]:
        """Get all items for a bill.

        Args:
            bill_id: ID of bill

        Returns:
            List of items
        """
        cursor = self.conn.execute(
            "SELECT id, bill_id, description, cost FROM items WHERE bill_id = ?",
            (bill_id,),
        )
        return [
            Item(
                id=row["id"],
                bill_id=row["bill_id"],
                description=row["description"],
                cost=Decimal(str(row["cost"])),
            )
            for row in cursor.fetchall()
        ]

    def delete(self, item_id: int) -> None:
        """Delete item by ID.

        Args:
            item_id: ID of item to delete
        """
        self.conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
        self.conn.commit()

    def update(self, item: Item) -> Item:
        """Update existing item.

        Args:
            item: Item with updated data (must have id)

        Returns:
            Updated item
        """
        if item.id is None:
            raise ValueError("Cannot update item without ID")

        self.conn.execute(
            "UPDATE items SET description = ?, cost = ? WHERE id = ?",
            (item.description, float(item.cost), item.id),
        )
        self.conn.commit()
        return item
