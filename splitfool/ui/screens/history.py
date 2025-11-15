"""History screen for viewing past bills."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Label, Static

from splitfool.models.bill import Bill
from splitfool.services.bill_service import BillDetail


class HistoryScreen(Screen[None]):
    """Screen for viewing bill history."""

    CSS = """
    HistoryScreen {
        background: $surface;
    }
    
    #title {
        text-style: bold;
        color: $accent;
        margin: 1;
        content-align: center middle;
    }
    
    #list-container {
        width: 90%;
        height: auto;
        margin: 1;
        border: solid $primary;
        padding: 1;
    }
    
    #bill-table {
        width: 100%;
        height: auto;
        max-height: 25;
    }
    
    #detail-container {
        width: 90%;
        height: auto;
        margin: 1;
        border: solid $accent;
        padding: 1;
    }
    
    #empty-message {
        width: 100%;
        content-align: center middle;
        color: $text-muted;
        padding: 2;
    }
    
    .detail-section {
        margin-bottom: 1;
    }
    
    .detail-label {
        text-style: bold;
        color: $accent;
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
        ("escape", "back", "Back"),
        ("r", "refresh", "Refresh"),
        ("b", "back_to_list", "Back to List"),
    ]

    def __init__(self) -> None:
        """Initialize history screen."""
        super().__init__()
        self.bills: list[Bill] = []
        self.selected_bill_id: int | None = None
        self.current_detail: BillDetail | None = None

    def compose(self) -> ComposeResult:
        """Compose history screen.

        Yields:
            Widgets for the screen
        """
        yield Header()

        with VerticalScroll():
            yield Label("📜 Bill History", id="title")

            with Container(id="list-container"):
                yield Static("Loading bills...", id="bill-content")

            # Detail container (hidden initially)
            with Container(id="detail-container") as detail:
                detail.display = False
                yield Static("", id="detail-content")

            with Horizontal(classes="button-row"):
                yield Button("🔄 Refresh [r]", id="refresh-btn", variant="primary")
                yield Button("⬅️  Back [esc]", id="back-btn", variant="default")

        yield Footer()

    async def on_mount(self) -> None:
        """Called when screen is mounted."""
        await self.load_bills()

    async def load_bills(self) -> None:
        """Load and display bill list."""
        from splitfool.ui.app import SplitfoolApp

        app = self.app
        assert isinstance(app, SplitfoolApp), "App must be SplitfoolApp"
        assert app.bill_service is not None, "BillService must be initialized"

        # Get all bills
        self.bills = app.bill_service.get_all_bills(limit=100)

        # Update display
        await self.update_bill_list()

    async def update_bill_list(self) -> None:
        """Update the bill list display."""
        from splitfool.ui.app import SplitfoolApp

        app = self.app
        assert isinstance(app, SplitfoolApp), "App must be SplitfoolApp"
        assert app.user_service is not None, "UserService must be initialized"

        container = self.query_one("#list-container", Container)
        
        # Remove old content
        try:
            old_content = container.query_one("#bill-content")
            await old_content.remove()
        except Exception:
            pass

        if not self.bills:
            # No bills - show empty message
            empty_msg = Static(
                "📭 No bills entered yet.\nCreate your first bill from the home screen!",
                id="bill-content",
                classes="empty-message",
            )
            await container.mount(empty_msg)
            return

        # Create table
        table: DataTable = DataTable(id="bill-content", cursor_type="row")
        table.add_columns("Date", "Description", "Payer", "Total")

        # Add bill rows
        for bill in self.bills:
            assert app.bill_service is not None
            payer = app.user_service.get_user(bill.payer_id)
            total = app.bill_service.calculate_total_cost(bill.id)  # type: ignore[arg-type]
            
            table.add_row(
                bill.created_at.strftime("%Y-%m-%d %H:%M"),
                bill.description[:40] + "..." if len(bill.description) > 40 else bill.description,
                payer.name if payer else "Unknown",
                f"${total:.2f}",
                key=str(bill.id),
            )

        await container.mount(table)

    async def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle bill row selection.

        Args:
            event: Row selected event
        """
        if event.row_key.value:
            bill_id = int(event.row_key.value)
            await self.show_bill_detail(bill_id)

    async def show_bill_detail(self, bill_id: int) -> None:
        """Show detailed view of a bill.

        Args:
            bill_id: ID of bill to show
        """
        from splitfool.ui.app import SplitfoolApp

        app = self.app
        assert isinstance(app, SplitfoolApp), "App must be SplitfoolApp"
        assert app.bill_service is not None, "BillService must be initialized"
        assert app.user_service is not None, "UserService must be initialized"

        # Get bill details
        self.current_detail = app.bill_service.get_bill(bill_id)
        if not self.current_detail:
            self.app.notify("Bill not found", severity="error")
            return

        self.selected_bill_id = bill_id

        # Format detail view
        detail_text = self._format_bill_detail(self.current_detail)

        # Update detail container
        detail_container = self.query_one("#detail-container", Container)
        detail_content = self.query_one("#detail-content", Static)
        detail_content.update(detail_text)
        detail_container.display = True

        # Hide list container
        list_container = self.query_one("#list-container", Container)
        list_container.display = False

    def _format_bill_detail(self, detail: BillDetail) -> str:
        """Format bill detail for display.

        Args:
            detail: Bill detail to format

        Returns:
            Formatted detail text
        """
        from splitfool.ui.app import SplitfoolApp

        app = self.app
        assert isinstance(app, SplitfoolApp), "App must be SplitfoolApp"
        assert app.user_service is not None, "UserService must be initialized"

        lines = []
        
        # Bill header
        lines.append(f"[bold cyan]Bill Details[/bold cyan]")
        lines.append("")
        lines.append(f"[bold]Description:[/bold] {detail.bill.description}")
        lines.append(f"[bold]Date:[/bold] {detail.bill.created_at.strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"[bold]Payer:[/bold] {detail.payer_name}")
        lines.append(f"[bold]Tax/Fees:[/bold] ${detail.bill.tax:.2f}")
        lines.append("")

        # Items
        lines.append("[bold cyan]Items:[/bold cyan]")
        for item, assignments in detail.items:
            lines.append(f"  • {item.description}: ${item.cost:.2f}")
            for assignment in assignments:
                user = app.user_service.get_user(assignment.user_id)
                if user:
                    fraction_pct = float(assignment.fraction * 100)
                    lines.append(f"    - {user.name}: {fraction_pct:.1f}%")
        lines.append("")

        # Calculated shares
        lines.append("[bold cyan]Calculated Shares:[/bold cyan]")
        for user_id, amount in detail.calculated_shares.items():
            user = app.user_service.get_user(user_id)
            if user:
                lines.append(f"  • {user.name}: ${amount:.2f}")
        lines.append("")

        # Total
        total = sum(item.cost for item, _ in detail.items) + detail.bill.tax
        lines.append(f"[bold]Total Bill: ${total:.2f}[/bold]")

        return "\n".join(lines)

    async def action_back_to_list(self) -> None:
        """Return to bill list view."""
        # Hide detail container
        detail_container = self.query_one("#detail-container", Container)
        detail_container.display = False

        # Show list container
        list_container = self.query_one("#list-container", Container)
        list_container.display = True

        self.selected_bill_id = None
        self.current_detail = None

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses.

        Args:
            event: Button pressed event
        """
        button_id = str(event.button.id)

        if button_id == "refresh-btn":
            await self.action_refresh()
        elif button_id == "back-btn":
            await self.action_back()

    async def action_refresh(self) -> None:
        """Refresh bill list."""
        await self.action_back_to_list()  # First go back to list if in detail view
        await self.load_bills()
        self.app.notify("Bill history refreshed", severity="information")

    async def action_back(self) -> None:
        """Return to home screen."""
        self.dismiss()
