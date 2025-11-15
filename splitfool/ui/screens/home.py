"""Home screen for main menu."""

from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Static


class HomeScreen(Screen[None]):
    """Home screen with main menu options."""

    CSS = """
    HomeScreen {
        align: center middle;
    }
    
    #menu {
        width: 60;
        height: auto;
        border: solid $primary;
        background: $surface;
        padding: 2;
    }
    
    #title {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }
    
    Button {
        width: 100%;
        margin: 1;
    }
    """

    BINDINGS = [
        ("u", "manage_users", "Manage Users"),
        ("b", "new_bill", "New Bill"),
        ("v", "view_balances", "View Balances"),
        ("h", "view_history", "View History"),
        ("escape", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Compose home screen.

        Yields:
            Screen widgets
        """
        with Container(id="menu"):
            yield Static("🧾 Splitfool", id="title")
            yield Static("Bill Splitting Application\n", id="subtitle")
            yield Button("👥 Manage Users [u]", id="btn-users", variant="primary")
            yield Button("💵 New Bill [b]", id="btn-bill", variant="default")
            yield Button("⚖️  View Balances [v]", id="btn-balances", variant="default")
            yield Button("📜 View History [h]", id="btn-history", variant="default")
            yield Button("❓ Help [?]", id="btn-help", variant="default")
            yield Button("🚪 Quit [q]", id="btn-quit", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses.

        Args:
            event: Button press event
        """
        button_id = event.button.id
        
        if button_id == "btn-users":
            self.action_manage_users()
        elif button_id == "btn-bill":
            self.action_new_bill()
        elif button_id == "btn-balances":
            self.action_view_balances()
        elif button_id == "btn-history":
            self.action_view_history()
        elif button_id == "btn-help":
            self.app.action_help()
        elif button_id == "btn-quit":
            self.app.exit()

    def action_manage_users(self) -> None:
        """Navigate to user management screen."""
        from splitfool.ui.screens.user_management import UserManagementScreen
        self.app.push_screen(UserManagementScreen())

    def action_new_bill(self) -> None:
        """Navigate to bill entry screen."""
        from splitfool.ui.screens.bill_entry import BillEntryScreen
        from splitfool.ui.app import SplitfoolApp
        
        app = self.app
        assert isinstance(app, SplitfoolApp), "App must be SplitfoolApp"
        
        # Get all users
        users = app.user_service.get_all_users()
        if not users:
            self.app.notify("No users found. Please add users first.", severity="error")
            return
        
        async def handle_bill_result(saved: bool) -> None:
            if saved:
                self.app.notify("Bill saved successfully!", severity="information")
        
        self.app.push_screen(BillEntryScreen(users), handle_bill_result)

    def action_view_balances(self) -> None:
        """Navigate to balance view screen."""
        from splitfool.ui.screens.balance_view import BalanceViewScreen
        
        self.app.push_screen(BalanceViewScreen())

    def action_view_history(self) -> None:
        """Navigate to history screen."""
        from splitfool.ui.screens.history import HistoryScreen
        
        self.app.push_screen(HistoryScreen())
