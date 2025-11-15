"""
Bill Service Contract

Defines the interface for bill creation and management operations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class Item:
    """Item entity."""
    id: int | None
    bill_id: int
    description: str
    cost: Decimal


@dataclass(frozen=True)
class Assignment:
    """Assignment entity linking items to users with fractions."""
    id: int | None
    item_id: int
    user_id: int
    fraction: Decimal


@dataclass(frozen=True)
class Bill:
    """Bill entity."""
    id: int | None
    payer_id: int
    description: str
    tax: Decimal
    created_at: datetime


@dataclass(frozen=True)
class BillDetail:
    """Complete bill with items and assignments for display."""
    bill: Bill
    items: list[tuple[Item, list[Assignment]]]  # Item with its assignments
    payer_name: str
    total_cost: Decimal
    user_shares: dict[int, Decimal]  # user_id -> amount owed


@dataclass(frozen=True)
class BillInput:
    """Input data for creating a bill."""
    payer_id: int
    description: str
    tax: Decimal
    items: list['ItemInput']


@dataclass(frozen=True)
class ItemInput:
    """Input data for a bill item."""
    description: str
    cost: Decimal
    assignments: list['AssignmentInput']


@dataclass(frozen=True)
class AssignmentInput:
    """Input data for an assignment."""
    user_id: int
    fraction: Decimal


class BillService(ABC):
    """
    Service for managing bills and calculating splits.
    
    Responsibilities:
    - Bill creation with validation (FR-008, FR-009)
    - Item and assignment management (FR-010, FR-011, FR-012, FR-013)
    - Tax distribution calculation (FR-014, FR-015)
    - Cost calculation and display (FR-017, FR-018)
    - Bill history retrieval (FR-030, FR-031, FR-032)
    """
    
    @abstractmethod
    def create_bill(self, bill_input: BillInput) -> BillDetail:
        """
        Create a new bill with items and assignments.
        
        Validates all input data and calculates splits before persisting.
        
        Args:
            bill_input: Complete bill data with items and assignments
            
        Returns:
            Created bill with calculated shares
            
        Raises:
            ValidationError: If any validation fails:
                - BILL_001: Payer doesn't exist
                - BILL_002: Tax is negative
                - BILL_003: No items provided (FR-049)
                - ITEM_001: Item cost not positive
                - ITEM_002: Item description empty/too long
                - ASSIGN_001: Fraction not in (0, 1] range
                - ASSIGN_002: Fractions don't sum to 1.0 for an item (FR-013)
                - ASSIGN_003: Item has no assignments (FR-050)
                - USER_NOT_FOUND: Assigned user doesn't exist
            
        Requirements: FR-008 through FR-023
        """
        pass
    
    @abstractmethod
    def get_bill(self, bill_id: int) -> BillDetail:
        """
        Retrieve a complete bill with all details.
        
        Args:
            bill_id: Bill's unique identifier
            
        Returns:
            Bill with items, assignments, and calculated shares
            
        Raises:
            BillNotFoundError: If bill doesn't exist
            
        Requirements: FR-031, FR-032
        """
        pass
    
    @abstractmethod
    def get_all_bills(self, limit: int | None = None, offset: int = 0) -> list[BillDetail]:
        """
        Retrieve all bills, most recent first.
        
        Args:
            limit: Maximum number of bills to return (None for all)
            offset: Number of bills to skip (for pagination)
            
        Returns:
            List of bills with full details, ordered by created_at DESC
            
        Requirements: FR-030 (chronological list)
        """
        pass
    
    @abstractmethod
    def calculate_user_share(
        self, 
        items: list[tuple[Item, list[Assignment]]], 
        tax: Decimal,
        user_id: int
    ) -> Decimal:
        """
        Calculate how much a specific user owes for a bill.
        
        Algorithm:
        1. Sum user's item costs: sum(item.cost × assignment.fraction)
        2. Calculate tax share: tax × (user_subtotal / bill_subtotal)
        3. Return user_subtotal + tax_share
        
        Args:
            items: List of items with their assignments
            tax: Total tax/additional costs
            user_id: User to calculate share for
            
        Returns:
            Amount user owes (rounded to 2 decimal places)
            
        Requirements: FR-015 (proportional tax), FR-018 (calculate shares), FR-023 (rounding)
        """
        pass
    
    @abstractmethod
    def calculate_total_cost(self, items: list[Item], tax: Decimal) -> Decimal:
        """
        Calculate total bill cost.
        
        Args:
            items: List of items
            tax: Tax/additional costs
            
        Returns:
            Sum of all item costs plus tax
            
        Requirements: FR-017
        """
        pass
    
    @abstractmethod
    def preview_bill(self, bill_input: BillInput) -> dict[int, Decimal]:
        """
        Preview how much each user would owe without saving the bill.
        
        Used during bill entry to show real-time calculations.
        
        Args:
            bill_input: Bill data to preview
            
        Returns:
            Dictionary mapping user_id to amount owed
            
        Raises:
            ValidationError: If bill data is invalid
            
        Requirements: FR-019 (modify before finalizing), FR-018 (see owed amounts)
        """
        pass
