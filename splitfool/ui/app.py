"""Main Textual application."""

import sqlite3
from typing import Any

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header

from splitfool.config import Config
from splitfool.db.connection import get_connection, initialize_database
from splitfool.services.balance_service import BalanceService
from splitfool.services.bill_service import BillService
from splitfool.services.user_service import UserService
from splitfool.ui.screens.home import HomeScreen


class SplitfoolApp(App[None]):
    """Splitfool TUI application."""

    CSS = """
    Screen {
        background: $surface;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("?", "help", "Help"),
    ]

    def __init__(self, config: Config | None = None) -> None:
        """Initialize application.

        Args:
            config: Application configuration
        """
        super().__init__()
        self.config = config or Config()
        self.conn: sqlite3.Connection | None = None
        self.user_service: UserService | None = None
        self.bill_service: BillService | None = None
        self.balance_service: BalanceService | None = None

    def on_mount(self) -> None:
        """Initialize application on mount."""
        # Initialize database
        initialize_database(self.config.db_path_str)
        
        # Create connection
        self.conn = get_connection(self.config.db_path_str)
        
        # Initialize services
        self.user_service = UserService(self.conn)
        self.bill_service = BillService(self.conn)
        self.balance_service = BalanceService(self.conn)
        
        # Wire up balance service to user service
        self.user_service.set_balance_service(self.balance_service)
        
        # Push home screen
        self.push_screen(HomeScreen())

    def compose(self) -> ComposeResult:
        """Compose app layout.

        Yields:
            App widgets
        """
        yield Header()
        yield Footer()

    def action_help(self) -> None:
        """Show help screen."""
        self.notify("Help screen not yet implemented")

    async def on_unmount(self) -> None:
        """Clean up resources on unmount."""
        if self.conn:
            self.conn.close()
