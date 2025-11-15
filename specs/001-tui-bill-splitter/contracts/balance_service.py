"""
Balance Service Contract

Defines the interface for balance calculation and settlement operations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class Balance:
    """Balance entity representing debt from one user to another."""
    debtor_id: int
    debtor_name: str
    creditor_id: int
    creditor_name: str
    amount: Decimal


@dataclass(frozen=True)
class Settlement:
    """Settlement record."""
    id: int | None
    settled_at: datetime
    note: str


class BalanceService(ABC):
    """
    Service for calculating balances and managing settlements.
    
    Responsibilities:
    - Calculate net balances between users (FR-024, FR-025)
    - Simplify mutual debts (FR-025)
    - Settlement management (FR-026, FR-027, FR-028)
    - Balance persistence check (FR-029)
    """
    
    @abstractmethod
    def get_all_balances(self) -> list[Balance]:
        """
        Calculate and return all outstanding balances.
        
        Algorithm:
        1. Get most recent settlement timestamp (if any)
        2. Fetch all bills created after settlement
        3. For each bill, calculate each user's share vs. what payer paid
        4. Aggregate debts: track all amounts user A owes user B
        5. Net out mutual debts: if A owes B $50 and B owes A $30, result is A owes B $20
        6. Return only non-zero balances
        
        Returns:
            List of net balances, sorted by debtor name then creditor name
            Empty list if all balances are zero
            
        Requirements: FR-024 (display balances), FR-025 (net format)
        """
        pass
    
    @abstractmethod
    def get_user_balances(self, user_id: int) -> tuple[list[Balance], list[Balance]]:
        """
        Get balances for a specific user.
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            Tuple of (debts, credits):
                - debts: Balances where user is the debtor
                - credits: Balances where user is the creditor
                
        Requirements: Support user detail view
        """
        pass
    
    @abstractmethod
    def user_has_outstanding_balances(self, user_id: int) -> bool:
        """
        Check if user has any non-zero balances.
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            True if user owes money or is owed money, False otherwise
            
        Requirements: FR-004 (prevent user deletion with balances)
        """
        pass
    
    @abstractmethod
    def preview_settlement(self) -> list[Balance]:
        """
        Preview what balances would be cleared by settlement.
        
        Returns:
            List of all current balances that would be cleared
            
        Requirements: FR-027 (confirmation summary before settlement)
        """
        pass
    
    @abstractmethod
    def settle_all_balances(self, note: str = "") -> Settlement:
        """
        Create a settlement record, effectively clearing all balances.
        
        Future balance calculations will only consider bills created after
        this settlement timestamp.
        
        Args:
            note: Optional note about the settlement
            
        Returns:
            Created settlement record
            
        Requirements: FR-026 (settle all), FR-028 (reset to zero), FR-029 (persist)
        """
        pass
    
    @abstractmethod
    def get_last_settlement(self) -> Settlement | None:
        """
        Get the most recent settlement.
        
        Returns:
            Most recent settlement, or None if no settlements exist
            
        Requirements: Support balance calculation (need cutoff date)
        """
        pass
    
    @abstractmethod
    def get_settlement_history(self) -> list[Settlement]:
        """
        Get all historical settlements.
        
        Returns:
            List of all settlements, most recent first
            
        Requirements: Support audit trail
        """
        pass
