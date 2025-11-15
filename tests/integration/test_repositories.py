"""Integration tests for database repositories."""

from datetime import datetime
from decimal import Decimal

import pytest

from splitfool.db.repositories import (
    AssignmentRepository,
    BillRepository,
    ItemRepository,
    UserRepository,
)
from splitfool.models import Assignment, Bill, Item, User
from splitfool.utils.errors import DuplicateUserError, UserNotFoundError
from tests.fixtures import in_memory_db


def test_user_repository_create(in_memory_db):  # type: ignore
    """Test creating a user."""
    repo = UserRepository(in_memory_db)
    user = User(id=None, name="Alice", created_at=datetime.now())
    
    created_user = repo.create(user)
    
    assert created_user.id is not None
    assert created_user.name == "Alice"


def test_user_repository_create_duplicate_name(in_memory_db):  # type: ignore
    """Test that creating duplicate user name raises error."""
    repo = UserRepository(in_memory_db)
    user1 = User(id=None, name="Alice", created_at=datetime.now())
    user2 = User(id=None, name="Alice", created_at=datetime.now())
    
    repo.create(user1)
    
    with pytest.raises(DuplicateUserError):
        repo.create(user2)


def test_user_repository_get(in_memory_db):  # type: ignore
    """Test retrieving a user by ID."""
    repo = UserRepository(in_memory_db)
    user = User(id=None, name="Alice", created_at=datetime.now())
    created_user = repo.create(user)
    
    retrieved_user = repo.get(created_user.id)  # type: ignore
    
    assert retrieved_user.id == created_user.id
    assert retrieved_user.name == "Alice"


def test_user_repository_get_not_found(in_memory_db):  # type: ignore
    """Test that getting non-existent user raises error."""
    repo = UserRepository(in_memory_db)
    
    with pytest.raises(UserNotFoundError):
        repo.get(999)


def test_user_repository_get_all(in_memory_db):  # type: ignore
    """Test retrieving all users."""
    repo = UserRepository(in_memory_db)
    user1 = User(id=None, name="Alice", created_at=datetime.now())
    user2 = User(id=None, name="Bob", created_at=datetime.now())
    
    repo.create(user1)
    repo.create(user2)
    
    all_users = repo.get_all()
    
    assert len(all_users) == 2
    assert all_users[0].name == "Alice"  # Sorted by name
    assert all_users[1].name == "Bob"


def test_user_repository_update(in_memory_db):  # type: ignore
    """Test updating a user."""
    repo = UserRepository(in_memory_db)
    user = User(id=None, name="Alice", created_at=datetime.now())
    created_user = repo.create(user)
    
    updated_user = created_user.replace(name="Alice Smith")
    result = repo.update(updated_user)
    
    assert result.name == "Alice Smith"
    retrieved = repo.get(created_user.id)  # type: ignore
    assert retrieved.name == "Alice Smith"


def test_user_repository_delete(in_memory_db):  # type: ignore
    """Test deleting a user."""
    repo = UserRepository(in_memory_db)
    user = User(id=None, name="Alice", created_at=datetime.now())
    created_user = repo.create(user)
    
    repo.delete(created_user.id)  # type: ignore
    
    with pytest.raises(UserNotFoundError):
        repo.get(created_user.id)  # type: ignore


def test_user_repository_exists_by_name(in_memory_db):  # type: ignore
    """Test checking if user exists by name."""
    repo = UserRepository(in_memory_db)
    user = User(id=None, name="Alice", created_at=datetime.now())
    
    assert not repo.exists_by_name("Alice")
    
    repo.create(user)
    
    assert repo.exists_by_name("Alice")
    assert not repo.exists_by_name("Bob")


def test_bill_repository_create(in_memory_db):  # type: ignore
    """Test creating a bill."""
    user_repo = UserRepository(in_memory_db)
    bill_repo = BillRepository(in_memory_db)
    
    user = user_repo.create(User(id=None, name="Alice", created_at=datetime.now()))
    bill = Bill(
        id=None,
        payer_id=user.id,  # type: ignore
        description="Dinner",
        tax=Decimal("10.50"),
        created_at=datetime.now(),
    )
    
    created_bill = bill_repo.create(bill)
    
    assert created_bill.id is not None
    assert created_bill.description == "Dinner"


def test_bill_repository_get_all(in_memory_db):  # type: ignore
    """Test retrieving all bills."""
    user_repo = UserRepository(in_memory_db)
    bill_repo = BillRepository(in_memory_db)
    
    user = user_repo.create(User(id=None, name="Alice", created_at=datetime.now()))
    
    bill1 = Bill(
        id=None,
        payer_id=user.id,  # type: ignore
        description="Bill 1",
        tax=Decimal("5.00"),
        created_at=datetime(2025, 1, 1),
    )
    bill2 = Bill(
        id=None,
        payer_id=user.id,  # type: ignore
        description="Bill 2",
        tax=Decimal("10.00"),
        created_at=datetime(2025, 1, 2),
    )
    
    bill_repo.create(bill1)
    bill_repo.create(bill2)
    
    all_bills = bill_repo.get_all()
    
    assert len(all_bills) == 2
    assert all_bills[0].description == "Bill 2"  # Newest first


def test_item_repository_create_and_get(in_memory_db):  # type: ignore
    """Test creating and retrieving items."""
    user_repo = UserRepository(in_memory_db)
    bill_repo = BillRepository(in_memory_db)
    item_repo = ItemRepository(in_memory_db)
    
    user = user_repo.create(User(id=None, name="Alice", created_at=datetime.now()))
    bill = bill_repo.create(
        Bill(
            id=None,
            payer_id=user.id,  # type: ignore
            description="Dinner",
            tax=Decimal("0"),
            created_at=datetime.now(),
        )
    )
    
    item = Item(
        id=None,
        bill_id=bill.id,  # type: ignore
        description="Pizza",
        cost=Decimal("25.00"),
    )
    created_item = item_repo.create(item)
    
    items = item_repo.get_by_bill(bill.id)  # type: ignore
    
    assert len(items) == 1
    assert items[0].description == "Pizza"


def test_assignment_repository_create_and_get(in_memory_db):  # type: ignore
    """Test creating and retrieving assignments."""
    user_repo = UserRepository(in_memory_db)
    bill_repo = BillRepository(in_memory_db)
    item_repo = ItemRepository(in_memory_db)
    assign_repo = AssignmentRepository(in_memory_db)
    
    user = user_repo.create(User(id=None, name="Alice", created_at=datetime.now()))
    bill = bill_repo.create(
        Bill(
            id=None,
            payer_id=user.id,  # type: ignore
            description="Dinner",
            tax=Decimal("0"),
            created_at=datetime.now(),
        )
    )
    item = item_repo.create(
        Item(
            id=None,
            bill_id=bill.id,  # type: ignore
            description="Pizza",
            cost=Decimal("25.00"),
        )
    )
    
    assignment = Assignment(
        id=None,
        item_id=item.id,  # type: ignore
        user_id=user.id,  # type: ignore
        fraction=Decimal("1.0"),
    )
    created_assignment = assign_repo.create(assignment)
    
    assignments = assign_repo.get_by_item(item.id)  # type: ignore
    
    assert len(assignments) == 1
    assert assignments[0].fraction == Decimal("1.0")


def test_assignment_repository_validate_fractions(in_memory_db):  # type: ignore
    """Test validating that fractions sum to 1.0."""
    user_repo = UserRepository(in_memory_db)
    bill_repo = BillRepository(in_memory_db)
    item_repo = ItemRepository(in_memory_db)
    assign_repo = AssignmentRepository(in_memory_db)
    
    user1 = user_repo.create(User(id=None, name="Alice", created_at=datetime.now()))
    user2 = user_repo.create(User(id=None, name="Bob", created_at=datetime.now()))
    bill = bill_repo.create(
        Bill(
            id=None,
            payer_id=user1.id,  # type: ignore
            description="Dinner",
            tax=Decimal("0"),
            created_at=datetime.now(),
        )
    )
    item = item_repo.create(
        Item(
            id=None,
            bill_id=bill.id,  # type: ignore
            description="Pizza",
            cost=Decimal("25.00"),
        )
    )
    
    # Create assignments that sum to 1.0
    assign_repo.create(
        Assignment(
            id=None,
            item_id=item.id,  # type: ignore
            user_id=user1.id,  # type: ignore
            fraction=Decimal("0.5"),
        )
    )
    assign_repo.create(
        Assignment(
            id=None,
            item_id=item.id,  # type: ignore
            user_id=user2.id,  # type: ignore
            fraction=Decimal("0.5"),
        )
    )
    
    assert assign_repo.validate_fractions_sum(item.id)  # type: ignore
