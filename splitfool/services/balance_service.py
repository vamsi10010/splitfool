"""Balance service for calculating and managing balances."""

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from splitfool.db.repositories.assignment_repository import AssignmentRepository
from splitfool.db.repositories.bill_repository import BillRepository
from splitfool.db.repositories.item_repository import ItemRepository
from splitfool.db.repositories.settlement_repository import SettlementRepository
from splitfool.db.repositories.user_repository import UserRepository
from splitfool.models.balance import Balance
from splitfool.models.settlement import Settlement
from splitfool.services.bill_service import BillService


@dataclass(frozen=True)
class BalancePreview:
    """Preview of balances before settlement."""

    balances: list[Balance]
    total_debts: Decimal


class BalanceService:
    """Service for balance calculation and settlement operations."""

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
        self.settlement_repo = SettlementRepository(connection)
        self.bill_service = BillService(connection)

    def get_all_balances(self) -> list[Balance]:
        """Calculate net balances from all bills since last settlement.

        Returns:
            List of non-zero balances showing who owes whom

        Algorithm:
            1. Get last settlement date (or beginning of time if none)
            2. Get all bills since that date
            3. For each bill, calculate each user's share
            4. Track what each user owes the payer
            5. Net out mutual debts
            6. Return only positive balances
        """
        # Get last settlement date
        last_settlement = self.settlement_repo.get_latest()
        cutoff_date = (
            last_settlement.settled_at if last_settlement else datetime.min
        )

        # Get all bills since last settlement
        bills = self.bill_repo.get_since_date(cutoff_date)

        if not bills:
            return []

        # Track gross debts: (debtor_id, creditor_id) -> amount
        gross_debts: dict[tuple[int, int], Decimal] = {}

        # Calculate debts for each bill
        for bill in bills:
            assert bill.id is not None, "Bill must have ID"
            
            # Get all users involved in this bill
            items = self.item_repo.get_by_bill(bill.id)
            user_ids: set[int] = set()
            for item in items:
                assert item.id is not None, "Item must have ID"
                assignments = self.assignment_repo.get_by_item(item.id)
                user_ids.update(a.user_id for a in assignments)

            # Calculate each user's share and debt to payer
            for user_id in user_ids:
                if user_id == bill.payer_id:
                    # Payer doesn't owe themselves
                    continue

                user_share = self.bill_service.calculate_user_share(bill.id, user_id)
                
                if user_share > Decimal("0"):
                    # User owes the payer
                    debt_key = (user_id, bill.payer_id)
                    gross_debts[debt_key] = (
                        gross_debts.get(debt_key, Decimal("0")) + user_share
                    )

        # Net out mutual debts
        return self._net_balances(gross_debts)

    def _net_balances(
        self, gross_debts: dict[tuple[int, int], Decimal]
    ) -> list[Balance]:
        """Net out mutual debts and return only non-zero balances.

        Args:
            gross_debts: Mapping of (debtor_id, creditor_id) -> amount

        Returns:
            List of net balances with positive amounts only
        """
        net_balances: dict[tuple[int, int], Decimal] = {}

        # Process all debt pairs
        processed: set[tuple[int, int]] = set()
        
        for (debtor_id, creditor_id), amount in gross_debts.items():
            if (debtor_id, creditor_id) in processed:
                continue

            # Check for reverse debt
            reverse_debt = gross_debts.get((creditor_id, debtor_id), Decimal("0"))

            # Net out the debts
            net_amount = amount - reverse_debt

            if net_amount > Decimal("0.01"):  # Only keep if > 1 cent
                net_balances[(debtor_id, creditor_id)] = net_amount
            elif net_amount < Decimal("-0.01"):  # Reverse direction
                net_balances[(creditor_id, debtor_id)] = -net_amount

            # Mark both directions as processed
            processed.add((debtor_id, creditor_id))
            processed.add((creditor_id, debtor_id))

        # Convert to Balance objects
        return [
            Balance(debtor_id=debtor, creditor_id=creditor, amount=amt)
            for (debtor, creditor), amt in sorted(net_balances.items())
        ]

    def get_user_balances(self, user_id: int) -> tuple[list[Balance], list[Balance]]:
        """Get balances for a specific user.

        Args:
            user_id: ID of user to query

        Returns:
            Tuple of (debts, credits) where:
                - debts: list of balances where user is debtor (owes money)
                - credits: list of balances where user is creditor (is owed money)
        """
        all_balances = self.get_all_balances()
        
        debts = [b for b in all_balances if b.debtor_id == user_id]
        credits = [b for b in all_balances if b.creditor_id == user_id]

        return debts, credits

    def user_has_outstanding_balances(self, user_id: int) -> bool:
        """Check if user has any outstanding balances.

        Args:
            user_id: ID of user to check

        Returns:
            True if user has any debts or credits
        """
        debts, credits = self.get_user_balances(user_id)
        return len(debts) > 0 or len(credits) > 0

    def preview_settlement(self) -> BalancePreview:
        """Preview current balances that would be cleared by settlement.

        Returns:
            Preview showing all current balances and total debt amount
        """
        balances = self.get_all_balances()
        total_debts = sum((b.amount for b in balances), Decimal("0"))

        return BalancePreview(balances=balances, total_debts=total_debts)

    def settle_all_balances(self, note: str = "") -> Settlement:
        """Settle all outstanding balances.

        Creates a settlement record with current timestamp. All balance
        calculations will use this timestamp as the cutoff date going forward.

        Args:
            note: Optional note about the settlement

        Returns:
            Created settlement record

        Note:
            This does NOT delete bills. Bills remain in history for audit purposes.
            Balances are calculated from bills after the most recent settlement.
        """
        settlement = Settlement(
            id=None,
            settled_at=datetime.now(),
            note=note,
        )

        return self.settlement_repo.create(settlement)

    def get_last_settlement(self) -> Settlement | None:
        """Get the most recent settlement.

        Returns:
            Most recent settlement or None if no settlements exist
        """
        return self.settlement_repo.get_latest()
