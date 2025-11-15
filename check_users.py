#!/usr/bin/env python3
"""Quick script to check what users are in the database."""

from splitfool.db.connection import get_connection
from splitfool.services.user_service import UserService

# Connect to database
conn = get_connection("splitfool.db")
service = UserService(conn)

# Get all users
users = service.get_all_users()

print("=" * 60)
print(f"Users in database: {len(users)}")
print("=" * 60)

if users:
    for user in users:
        print(f"ID: {user.id}")
        print(f"Name: {user.name}")
        print(f"Created: {user.created_at}")
        print("-" * 60)
else:
    print("No users found!")

conn.close()
