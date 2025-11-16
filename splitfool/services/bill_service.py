"""Bill service for business logic operations."""

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from splitfool.db.repositories.assignment_repository import AssignmentRepository
from splitfool.db.repositories.bill_repository import BillRepository
from splitfool.db.repositories.item_repository import ItemRepository
from splitfool.db.repositories.user_repository import UserRepository
from splitfool.models.assignment import Assignment
from splitfool.models.bill import Bill
from splitfool.models.item import Item
from splitfool.utils.errors import BillNotFoundError, UserNotFoundError, ValidationError


@dataclass(frozen=True)
class ItemInput:
    """Input data for creating an item."""

    description: str
    cost: Decimal
    assignments: list["AssignmentInput"]


@dataclass(frozen=True)
class AssignmentInput:
    """Input data for creating an assignment."""

    user_id: int
    fraction: Decimal


@dataclass(frozen=True)
class BillInput:
    """Input data for creating a bill."""

    payer_id: int
    description: str
    tax: Decimal
    items: list[ItemInput]


@dataclass(frozen=True)
class BillDetail:
    """Complete bill details with items and assignments."""

    bill: Bill
    items: list[tuple[Item, list[Assignment]]]
    payer_name: str
    calculated_shares: dict[int, Decimal]


@dataclass(frozen=True)
class BillPreview:
    """Preview of bill calculations before saving."""

    description: str
    payer_name: str
    subtotal: Decimal
    tax: Decimal
    total: Decimal
    user_shares: dict[str, Decimal]  # user_name -> amount


class BillService:
    """Service for bill-related operations."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        """Initialize service with database connection.

        Args:
            connection: SQLite database connection
        """
        self.conn = connection
        self.bill_repo = BillRepository(connection)
        self.item_repo = ItemRepository(connection)
        self.assignment_repo = AssignmentRepository(connection)
        self.user_repo = UserRepository(connection)

    def create_bill(self, bill_input: BillInput) -> Bill:
        """Create a bill with items and assignments.

        Args:
            bill_input: Bill creation data

        Returns:
            Created bill

        Raises:
            ValidationError: If validation fails
            UserNotFoundError: If payer doesn't exist
        """
        # Validate payer exists
        payer = self.user_repo.get(bill_input.payer_id)
        if payer is None:
            raise UserNotFoundError(
                f"Payer with ID {bill_input.payer_id} not found", code="BILL_002"
            )

        # Validate at least one item
        if not bill_input.items:
            raise ValidationError("Bill must have at least one item", code="BILL_004")

        # Validate tax non-negative
        if bill_input.tax < Decimal("0"):
            raise ValidationError("Tax must be non-negative", code="BILL_003")

        # Validate all items and assignments
        for item_input in bill_input.items:
            # Validate item cost positive
            if item_input.cost <= Decimal("0"):
                raise ValidationError(
                    f"Item '{item_input.description}' cost must be positive", code="ITEM_001"
                )

            # Validate item description non-empty
            if not item_input.description or item_input.description.isspace():
                raise ValidationError("Item description cannot be empty", code="ITEM_002")

            # Validate at least one assignment per item
            if not item_input.assignments:
                raise ValidationError(
                    f"Item '{item_input.description}' must have at least one assignment",
                    code="ASSIGN_003",
                )

            # Validate fractions sum to 1.0
            total_fraction = sum(a.fraction for a in item_input.assignments)
            if abs(total_fraction - Decimal("1.0")) > Decimal("0.001"):
                raise ValidationError(
                    f"Item '{item_input.description}' fractions sum to {total_fraction}, "
                    f"must equal 1.0",
                    code="ASSIGN_002",
                )

            # Validate all assigned users exist
            for assignment_input_item in item_input.assignments:
                user = self.user_repo.get(assignment_input_item.user_id)
                if user is None:
                    raise UserNotFoundError(
                        f"User with ID {assignment_input_item.user_id} not found",
                        code="BILL_002",
                    )

                # Validate fraction range
                if not (Decimal("0") < assignment_input_item.fraction <= Decimal("1")):
                    raise ValidationError(
                        "Assignment fraction must be between 0 and 1", code="ASSIGN_001"
                    )

        # Create bill, items, and assignments in transaction
        try:
            # Create bill
            bill = Bill(
                id=None,
                payer_id=bill_input.payer_id,
                description=bill_input.description,
                tax=bill_input.tax,
                created_at=datetime.now(),
            )
            created_bill = self.bill_repo.create(bill)

            # Create items and assignments
            for item_input in bill_input.items:
                assert created_bill.id is not None, "Bill ID should be set after creation"
                item = Item(
                    id=None,
                    bill_id=created_bill.id,
                    description=item_input.description,
                    cost=item_input.cost,
                )
                created_item = self.item_repo.create(item)
                assert created_item.id is not None, "Item ID should be set after creation"

                for assignment_input in item_input.assignments:
                    assignment = Assignment(
                        id=None,
                        item_id=created_item.id,
                        user_id=assignment_input.user_id,
                        fraction=assignment_input.fraction,
                    )
                    self.assignment_repo.create(assignment)

            return created_bill
        except Exception as e:
            self.conn.rollback()
            raise e

    def calculate_user_share(self, bill_id: int, user_id: int) -> Decimal:
        """Calculate a user's share of a bill.

        Args:
            bill_id: ID of bill
            user_id: ID of user

        Returns:
            User's total share (items + proportional tax)

        Raises:
            BillNotFoundError: If bill doesn't exist

        Algorithm: Proportional Tax Distribution
        -----------------------------------------
        Tax (tip/fees) is distributed proportionally based on each user's
        share of the bill's item costs.

        Example:
        - Pizza $30 → Alice 100%  = $30.00
        - Salad $15 → Bob 50%, Carol 50% = $7.50 each
        - Tax $12
        - Subtotal = $30 + $15 = $45
        - Alice's share: $30/$45 × $12 = $8.00 tax
        - Bob's share: $7.50/$45 × $12 = $2.00 tax
        - Carol's share: $7.50/$45 × $12 = $2.00 tax

        This ensures tax is distributed fairly based on actual consumption,
        not equally among all participants.
        """
        bill = self.bill_repo.get(bill_id)
        if bill is None:
            raise BillNotFoundError(f"Bill with ID {bill_id} not found", code="BILL_001")

        items = self.item_repo.get_by_bill(bill_id)
        subtotal = Decimal("0")  # Total cost of all items
        user_subtotal = Decimal("0")  # User's portion of item costs

        # Calculate user's share of item costs based on assigned fractions
        for item in items:
            subtotal += item.cost
            assignments = self.assignment_repo.get_by_item(item.id)  # type: ignore
            for assignment in assignments:
                if assignment.user_id == user_id:
                    # Add user's fractional share of this item
                    # Example: $30 item × 0.5 fraction = $15 for this user
                    user_subtotal += item.cost * assignment.fraction

        # Distribute tax proportionally based on user's share of item costs
        # Formula: user_tax = total_tax × (user_items / total_items)
        if subtotal > Decimal("0"):
            tax_share = bill.tax * (user_subtotal / subtotal)
        else:
            tax_share = Decimal("0")  # No items means no tax

        return user_subtotal + tax_share

    def calculate_total_cost(self, bill_id: int) -> Decimal:
        """Calculate total cost of a bill.

        Args:
            bill_id: ID of bill

        Returns:
            Total cost (items + tax)

        Raises:
            BillNotFoundError: If bill doesn't exist
        """
        bill = self.bill_repo.get(bill_id)
        if bill is None:
            raise BillNotFoundError(f"Bill with ID {bill_id} not found", code="BILL_001")

        items = self.item_repo.get_by_bill(bill_id)
        subtotal = sum(item.cost for item in items)

        return subtotal + bill.tax

    def preview_bill(self, bill_input: BillInput) -> BillPreview:
        """Preview bill calculations without saving.

        Args:
            bill_input: Bill data to preview

        Returns:
            Preview with calculated shares

        Raises:
            ValidationError: If validation fails
            UserNotFoundError: If payer or assigned users don't exist
        """
        # Validate payer exists
        payer = self.user_repo.get(bill_input.payer_id)
        if payer is None:
            raise UserNotFoundError(
                f"Payer with ID {bill_input.payer_id} not found", code="BILL_002"
            )

        # Validate items exist
        if not bill_input.items:
            raise ValidationError("Bill must have at least one item", code="BILL_004")

        # Calculate subtotal
        subtotal: Decimal = sum((item.cost for item in bill_input.items), Decimal("0"))
        total = subtotal + bill_input.tax

        # Calculate each user's share
        user_shares: dict[int, Decimal] = {}
        for item_input in bill_input.items:
            for assignment in item_input.assignments:
                if assignment.user_id not in user_shares:
                    user_shares[assignment.user_id] = Decimal("0")
                user_shares[assignment.user_id] += item_input.cost * assignment.fraction

        # Add proportional tax to each user
        if subtotal > Decimal("0"):
            for user_id, user_subtotal in user_shares.items():
                tax_share = bill_input.tax * (user_subtotal / subtotal)
                user_shares[user_id] += tax_share

        # Convert user IDs to names
        user_share_names: dict[str, Decimal] = {}
        for user_id, amount in user_shares.items():
            user = self.user_repo.get(user_id)
            if user is None:
                raise UserNotFoundError(f"User with ID {user_id} not found", code="BILL_002")
            user_share_names[user.name] = amount

        return BillPreview(
            description=bill_input.description,
            payer_name=payer.name,
            subtotal=subtotal,
            tax=bill_input.tax,
            total=total,
            user_shares=user_share_names,
        )

    def get_bill(self, bill_id: int) -> BillDetail | None:
        """Get complete bill details with items and assignments.

        Args:
            bill_id: ID of bill

        Returns:
            Complete bill details or None if not found
        """
        bill = self.bill_repo.get(bill_id)
        if bill is None:
            return None

        items = self.item_repo.get_by_bill(bill_id)
        items_with_assignments: list[tuple[Item, list[Assignment]]] = []

        for item in items:
            assignments = self.assignment_repo.get_by_item(item.id)  # type: ignore
            items_with_assignments.append((item, assignments))

        # Get payer name
        payer = self.user_repo.get(bill.payer_id)
        payer_name = payer.name if payer else "Unknown"

        # Calculate shares for all users
        all_users = self.user_repo.get_all()
        calculated_shares: dict[int, Decimal] = {}
        for user in all_users:
            share = self.calculate_user_share(bill_id, user.id)  # type: ignore
            if share > Decimal("0"):
                calculated_shares[user.id] = share  # type: ignore

        return BillDetail(
            bill=bill,
            items=items_with_assignments,
            payer_name=payer_name,
            calculated_shares=calculated_shares,
        )

    def get_all_bills(self, limit: int = 100, offset: int = 0) -> list[Bill]:
        """Get all bills with pagination.

        Args:
            limit: Maximum number of bills to return
            offset: Number of bills to skip

        Returns:
            List of bills ordered by created_at DESC (most recent first)
        """
        all_bills = self.bill_repo.get_all()
        # Sort by creation date, most recent first
        sorted_bills = sorted(all_bills, key=lambda b: b.created_at, reverse=True)
        # Apply pagination
        return sorted_bills[offset : offset + limit]
