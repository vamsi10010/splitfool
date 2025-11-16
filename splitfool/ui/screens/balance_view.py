"""Balance view screen for displaying outstanding balances."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Label, Static

from splitfool.models.balance import Balance


class BalanceViewScreen(Screen[bool]):
    """Screen for viewing outstanding balances and settling."""

    CSS = """
    BalanceViewScreen {
        background: $surface;
    }

    #title {
        text-style: bold;
        color: $accent;
        margin: 1;
        content-align: center middle;
    }

    #balance-container {
        width: 80%;
        height: auto;
        margin: 1;
        border: solid $primary;
        padding: 1;
    }

    #balance-table {
        width: 100%;
        height: auto;
        max-height: 30;
    }

    #empty-message {
        width: 100%;
        content-align: center middle;
        color: $success;
        text-style: bold;
        padding: 2;
    }

    #settlement-info {
        width: 100%;
        margin-top: 1;
        padding: 1;
        color: $text-muted;
    }

    .button-row {
        width: 100%;
        height: auto;
        align: center middle;
        margin-top: 1;
    }

    Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        ("escape", "cancel", "Back"),
        ("s", "settle", "Settle All"),
        ("r", "refresh", "Refresh"),
    ]

    def __init__(self) -> None:
        """Initialize balance view screen."""
        super().__init__()
        self.balances: list[Balance] = []

    def compose(self) -> ComposeResult:
        """Compose balance view screen.

        Yields:
            Widgets for the screen
        """
        yield Header()

        with VerticalScroll():
            yield Label("⚖️  Outstanding Balances", id="title")

            with Container(id="balance-container"):
                # Table will be dynamically created
                yield Static("Loading balances...", id="balance-content")

            yield Static("", id="settlement-info")

            with Horizontal(classes="button-row"):
                yield Button("🔄 Refresh [r]", id="refresh-btn", variant="primary")
                yield Button("✅ Settle All [s]", id="settle-btn", variant="success")
                yield Button("⬅️  Back [esc]", id="back-btn", variant="default")

        yield Footer()

    async def on_mount(self) -> None:
        """Called when screen is mounted."""
        await self.load_balances()

    async def load_balances(self) -> None:
        """Load and display current balances."""
        from splitfool.ui.app import SplitfoolApp

        app = self.app
        assert isinstance(app, SplitfoolApp), "App must be SplitfoolApp"
        assert app.balance_service is not None, "BalanceService must be initialized"

        # Get balances
        self.balances = app.balance_service.get_all_balances()

        # Get last settlement info
        last_settlement = app.balance_service.get_last_settlement()
        settlement_text = ""
        if last_settlement:
            settlement_text = (
                f"Last settlement: {last_settlement.settled_at.strftime('%Y-%m-%d %H:%M')}"
            )
            if last_settlement.note:
                settlement_text += f" - {last_settlement.note}"
        else:
            settlement_text = "No previous settlements"

        settlement_info = self.query_one("#settlement-info", Static)
        settlement_info.update(settlement_text)

        # Update display
        await self.update_balance_display()

    async def update_balance_display(self) -> None:
        """Update the balance display."""
        from splitfool.ui.app import SplitfoolApp

        app = self.app
        assert isinstance(app, SplitfoolApp), "App must be SplitfoolApp"
        assert app.user_service is not None, "UserService must be initialized"

        container = self.query_one("#balance-container", Container)

        # Remove old content
        try:
            old_content = container.query_one("#balance-content")
            await old_content.remove()
        except Exception:
            pass

        if not self.balances:
            # No balances - show success message
            empty_msg = Static(
                "🎉 All balances settled!\nNo outstanding debts.",
                id="balance-content",
                classes="empty-message",
            )
            await container.mount(empty_msg)

            # Disable settle button
            settle_btn = self.query_one("#settle-btn", Button)
            settle_btn.disabled = True
            return

        # Create table
        table: DataTable = DataTable(id="balance-content")
        table.add_columns("Debtor", "Creditor", "Amount")

        # Add balance rows
        for balance in self.balances:
            debtor = app.user_service.get_user(balance.debtor_id)
            creditor = app.user_service.get_user(balance.creditor_id)

            if debtor and creditor:
                table.add_row(
                    debtor.name,
                    creditor.name,
                    f"${balance.amount:.2f}",
                )

        await container.mount(table)

        # Enable settle button
        settle_btn = self.query_one("#settle-btn", Button)
        settle_btn.disabled = False

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses.

        Args:
            event: Button pressed event
        """
        button_id = str(event.button.id)

        if button_id == "refresh-btn":
            await self.action_refresh()
        elif button_id == "settle-btn":
            await self.action_settle()
        elif button_id == "back-btn":
            await self.action_cancel()

    async def action_refresh(self) -> None:
        """Refresh balance display."""
        await self.load_balances()
        self.app.notify("Balances refreshed", severity="information")

    async def action_settle(self) -> None:
        """Initiate settlement with confirmation."""
        if not self.balances:
            self.app.notify("No balances to settle", severity="warning")
            return

        # Show confirmation dialog
        from splitfool.ui.widgets.confirmation_dialog import ConfirmationDialog

        preview = self._format_settlement_preview()

        def handle_confirmation(confirmed: bool) -> None:
            """Handle settlement confirmation."""
            if confirmed:
                self.call_later(self.perform_settlement)

        dialog = ConfirmationDialog(
            title="Settle All Balances",
            message=preview,
            confirm_label="Settle",
            cancel_label="Cancel",
        )
        self.app.push_screen(dialog, handle_confirmation)

    def _format_settlement_preview(self) -> str:
        """Format preview of balances to be settled.

        Returns:
            Formatted preview text
        """
        from splitfool.ui.app import SplitfoolApp

        app = self.app
        assert isinstance(app, SplitfoolApp), "App must be SplitfoolApp"
        assert app.user_service is not None, "UserService must be initialized"

        lines = ["The following balances will be cleared:", ""]

        for balance in self.balances:
            debtor = app.user_service.get_user(balance.debtor_id)
            creditor = app.user_service.get_user(balance.creditor_id)

            if debtor and creditor:
                lines.append(f"  • {debtor.name} owes {creditor.name}: ${balance.amount:.2f}")

        lines.append("")
        total = sum(b.amount for b in self.balances)
        lines.append(f"Total debts: ${total:.2f}")
        lines.append("")
        lines.append("Are you sure you want to settle all balances?")

        return "\n".join(lines)

    async def perform_settlement(self) -> None:
        """Perform the actual settlement."""
        from splitfool.ui.app import SplitfoolApp

        app = self.app
        assert isinstance(app, SplitfoolApp), "App must be SplitfoolApp"
        assert app.balance_service is not None, "BalanceService must be initialized"

        try:
            # Create settlement record
            app.balance_service.settle_all_balances(
                note="Manual settlement via TUI"
            )

            # Reload balances
            await self.load_balances()

            # Show success notification
            self.app.notify(
                "✅ All balances settled successfully!",
                severity="information",
            )

        except Exception as e:
            self.app.notify(f"Error settling balances: {str(e)}", severity="error")

    async def action_cancel(self) -> None:
        """Return to home screen."""
        self.dismiss(False)
