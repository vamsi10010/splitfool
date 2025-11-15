"""Test fixtures for Splitfool tests."""

import sqlite3
from datetime import datetime
from decimal import Decimal

import pytest

from splitfool.db.connection import initialize_database
from splitfool.models import Assignment, Bill, Item, User


@pytest.fixture
def in_memory_db() -> sqlite3.Connection:
    """Create an in-memory SQLite database for testing.

    Yields:
        SQLite connection to in-memory database
    """
    initialize_database(":memory:")
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    
    # Initialize schema
    from splitfool.db.schema import SCHEMA_SQL
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    
    yield conn
    conn.close()


@pytest.fixture
def sample_user() -> User:
    """Create a sample user for testing.

    Returns:
        Sample User instance
    """
    return User(
        id=None,
        name="Alice",
        created_at=datetime(2025, 1, 1, 12, 0, 0),
    )


@pytest.fixture
def sample_bill() -> Bill:
    """Create a sample bill for testing.

    Returns:
        Sample Bill instance
    """
    return Bill(
        id=None,
        payer_id=1,
        description="Dinner at Restaurant",
        tax=Decimal("10.50"),
        created_at=datetime(2025, 1, 15, 18, 30, 0),
    )


@pytest.fixture
def sample_item() -> Item:
    """Create a sample item for testing.

    Returns:
        Sample Item instance
    """
    return Item(
        id=None,
        bill_id=1,
        description="Pizza",
        cost=Decimal("25.00"),
    )


@pytest.fixture
def sample_assignment() -> Assignment:
    """Create a sample assignment for testing.

    Returns:
        Sample Assignment instance
    """
    return Assignment(
        id=None,
        item_id=1,
        user_id=1,
        fraction=Decimal("0.5"),
    )
