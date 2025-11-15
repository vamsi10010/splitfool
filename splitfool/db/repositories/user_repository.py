"""User repository for database operations."""

import sqlite3
from datetime import datetime

from splitfool.models.user import User
from splitfool.utils.errors import DuplicateUserError, UserNotFoundError


class UserRepository:
    """Repository for User entity database operations."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        """Initialize repository with database connection.

        Args:
            connection: SQLite database connection
        """
        self.conn = connection

    def create(self, user: User) -> User:
        """Create a new user in the database.

        Args:
            user: User to create (id should be None)

        Returns:
            Created user with assigned ID

        Raises:
            DuplicateUserError: If user with same name already exists
        """
        try:
            cursor = self.conn.execute(
                "INSERT INTO users (name, created_at) VALUES (?, ?)",
                (user.name, user.created_at),
            )
            self.conn.commit()
            return user.replace(id=cursor.lastrowid)
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                raise DuplicateUserError(
                    f"User with name '{user.name}' already exists",
                    code="USER_003",
                ) from e
            raise

    def get(self, user_id: int) -> User:
        """Get user by ID.

        Args:
            user_id: ID of user to retrieve

        Returns:
            User instance

        Raises:
            UserNotFoundError: If user not found
        """
        cursor = self.conn.execute(
            "SELECT id, name, created_at FROM users WHERE id = ?",
            (user_id,),
        )
        row = cursor.fetchone()
        if not row:
            raise UserNotFoundError(
                f"User with ID {user_id} not found",
                code="USER_004",
            )
        return User(
            id=row["id"],
            name=row["name"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def get_all(self) -> list[User]:
        """Get all users.

        Returns:
            List of all users
        """
        cursor = self.conn.execute(
            "SELECT id, name, created_at FROM users ORDER BY name"
        )
        return [
            User(
                id=row["id"],
                name=row["name"],
                created_at=datetime.fromisoformat(row["created_at"]),
            )
            for row in cursor.fetchall()
        ]

    def update(self, user: User) -> User:
        """Update existing user.

        Args:
            user: User with updated data (must have id)

        Returns:
            Updated user

        Raises:
            UserNotFoundError: If user not found
            DuplicateUserError: If new name conflicts with existing user
        """
        if user.id is None:
            raise ValueError("Cannot update user without ID")
        
        try:
            cursor = self.conn.execute(
                "UPDATE users SET name = ? WHERE id = ?",
                (user.name, user.id),
            )
            if cursor.rowcount == 0:
                raise UserNotFoundError(
                    f"User with ID {user.id} not found",
                    code="USER_004",
                )
            self.conn.commit()
            return user
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                raise DuplicateUserError(
                    f"User with name '{user.name}' already exists",
                    code="USER_003",
                ) from e
            raise

    def delete(self, user_id: int) -> None:
        """Delete user by ID.

        Args:
            user_id: ID of user to delete

        Raises:
            UserNotFoundError: If user not found
        """
        cursor = self.conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        if cursor.rowcount == 0:
            raise UserNotFoundError(
                f"User with ID {user_id} not found",
                code="USER_004",
            )
        self.conn.commit()

    def exists_by_name(self, name: str) -> bool:
        """Check if user with given name exists.

        Args:
            name: User name to check

        Returns:
            True if user exists, False otherwise
        """
        cursor = self.conn.execute(
            "SELECT COUNT(*) as count FROM users WHERE name = ?",
            (name,),
        )
        row = cursor.fetchone()
        return row["count"] > 0
