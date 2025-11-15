"""Integration tests for complete user management workflow."""

from datetime import datetime

import pytest

from splitfool.db.connection import get_connection, initialize_database
from splitfool.services.user_service import UserService
from splitfool.utils.errors import DuplicateUserError, UserNotFoundError


def test_complete_user_workflow_with_persistence(tmp_path):  # type: ignore
    """Test complete user workflow: create, read, update, delete with persistence."""
    # Setup: Create database file
    db_path = str(tmp_path / "test.db")
    initialize_database(db_path)
    
    # Step 1: Create users
    conn = get_connection(db_path)
    service = UserService(conn)
    
    alice = service.create_user("Alice")
    bob = service.create_user("Bob")
    charlie = service.create_user("Charlie")
    
    assert alice.id is not None
    assert bob.id is not None
    assert charlie.id is not None
    
    conn.close()
    
    # Step 2: Verify persistence - reopen connection
    conn = get_connection(db_path)
    service = UserService(conn)
    
    all_users = service.get_all_users()
    assert len(all_users) == 3
    assert all_users[0].name == "Alice"
    assert all_users[1].name == "Bob"
    assert all_users[2].name == "Charlie"
    
    conn.close()
    
    # Step 3: Update user
    conn = get_connection(db_path)
    service = UserService(conn)
    
    updated_alice = service.update_user(alice.id, "Alice Smith")  # type: ignore
    assert updated_alice.name == "Alice Smith"
    
    conn.close()
    
    # Step 4: Verify update persisted
    conn = get_connection(db_path)
    service = UserService(conn)
    
    retrieved_alice = service.get_user(alice.id)  # type: ignore
    assert retrieved_alice.name == "Alice Smith"
    
    conn.close()
    
    # Step 5: Delete user
    conn = get_connection(db_path)
    service = UserService(conn)
    
    service.delete_user(charlie.id)  # type: ignore
    
    remaining_users = service.get_all_users()
    assert len(remaining_users) == 2
    assert "Charlie" not in [u.name for u in remaining_users]
    
    conn.close()
    
    # Step 6: Verify deletion persisted
    conn = get_connection(db_path)
    service = UserService(conn)
    
    final_users = service.get_all_users()
    assert len(final_users) == 2
    
    with pytest.raises(UserNotFoundError):
        service.get_user(charlie.id)  # type: ignore
    
    conn.close()


def test_user_workflow_validates_business_rules(tmp_path):  # type: ignore
    """Test that user workflow enforces business rules."""
    db_path = str(tmp_path / "test.db")
    initialize_database(db_path)
    
    conn = get_connection(db_path)
    service = UserService(conn)
    
    # Create initial user
    alice = service.create_user("Alice")
    
    # Test duplicate name rejection
    with pytest.raises(DuplicateUserError):
        service.create_user("Alice")
    
    # Test update to duplicate name rejection
    bob = service.create_user("Bob")
    
    with pytest.raises(DuplicateUserError):
        service.update_user(bob.id, "Alice")  # type: ignore
    
    # Test deletion of non-existent user
    with pytest.raises(UserNotFoundError):
        service.delete_user(999)
    
    conn.close()


def test_user_workflow_with_multiple_connections(tmp_path):  # type: ignore
    """Test that changes are visible across multiple connections."""
    db_path = str(tmp_path / "test.db")
    initialize_database(db_path)
    
    # Connection 1: Create users
    conn1 = get_connection(db_path)
    service1 = UserService(conn1)
    alice = service1.create_user("Alice")
    conn1.close()
    
    # Connection 2: Read users
    conn2 = get_connection(db_path)
    service2 = UserService(conn2)
    users = service2.get_all_users()
    assert len(users) == 1
    assert users[0].name == "Alice"
    conn2.close()
    
    # Connection 3: Update user
    conn3 = get_connection(db_path)
    service3 = UserService(conn3)
    service3.update_user(alice.id, "Alice Updated")  # type: ignore
    conn3.close()
    
    # Connection 4: Verify update
    conn4 = get_connection(db_path)
    service4 = UserService(conn4)
    updated_user = service4.get_user(alice.id)  # type: ignore
    assert updated_user.name == "Alice Updated"
    conn4.close()


def test_user_workflow_empty_database(tmp_path):  # type: ignore
    """Test user workflow starting with empty database."""
    db_path = str(tmp_path / "test.db")
    initialize_database(db_path)
    
    conn = get_connection(db_path)
    service = UserService(conn)
    
    # Initially empty
    users = service.get_all_users()
    assert len(users) == 0
    
    # Add first user
    alice = service.create_user("Alice")
    assert alice.id == 1  # First user gets ID 1
    
    users = service.get_all_users()
    assert len(users) == 1
    
    conn.close()


def test_user_workflow_data_integrity(tmp_path):  # type: ignore
    """Test that user data maintains integrity throughout workflow."""
    db_path = str(tmp_path / "test.db")
    initialize_database(db_path)
    
    conn = get_connection(db_path)
    service = UserService(conn)
    
    # Create user and verify all fields
    alice = service.create_user("Alice")
    
    assert alice.id is not None
    assert alice.name == "Alice"
    assert isinstance(alice.created_at, datetime)
    
    # Retrieve and verify fields match
    retrieved = service.get_user(alice.id)  # type: ignore
    
    assert retrieved.id == alice.id
    assert retrieved.name == alice.name
    assert retrieved.created_at == alice.created_at
    
    # Update and verify immutability of original
    updated = service.update_user(alice.id, "Alice Smith")  # type: ignore
    
    assert alice.name == "Alice"  # Original unchanged (immutable)
    assert updated.name == "Alice Smith"  # New instance updated
    assert updated.id == alice.id  # Same ID
    
    conn.close()


def test_user_workflow_multiple_operations(tmp_path):  # type: ignore
    """Test multiple add/delete operations in sequence."""
    db_path = str(tmp_path / "test.db")
    initialize_database(db_path)
    
    conn = get_connection(db_path)
    service = UserService(conn)
    
    # Add users
    alice = service.create_user("Alice")
    bob = service.create_user("Bob")
    charlie = service.create_user("Charlie")
    
    # Verify all 3 exist
    users = service.get_all_users()
    assert len(users) == 3
    
    # Delete one
    service.delete_user(bob.id)  # type: ignore
    
    # Verify 2 remain
    users = service.get_all_users()
    assert len(users) == 2
    assert "Bob" not in [u.name for u in users]
    
    # Add another
    dave = service.create_user("Dave")
    
    # Verify 3 total
    users = service.get_all_users()
    assert len(users) == 3
    
    conn.close()
