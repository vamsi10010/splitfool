"""Debug version to trace user loading."""

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import DataTable, Header, Footer, Static

from splitfool.db.connection import get_connection
from splitfool.services.user_service import UserService


class DebugApp(App):
    """Debug app to test table display."""

    def compose(self) -> ComposeResult:
        """Compose layout."""
        yield Header()
        yield Static("Debug: User Table Test", id="title")
        yield Container(
            DataTable(id="user-table"),
            id="table-container"
        )
        yield Footer()

    def on_mount(self) -> None:
        """Initialize on mount."""
        table = self.query_one("#user-table", DataTable)
        
        # Add columns
        self.notify("Adding columns...")
        table.add_columns("ID", "Name", "Created")
        self.notify(f"Columns added: {len(table.columns)}")
        
        # Load users from database
        self.notify("Loading users from database...")
        conn = get_connection("splitfool.db")
        service = UserService(conn)
        users = service.get_all_users()
        self.notify(f"Found {len(users)} users in database")
        
        # Add rows
        for user in users:
            created_str = user.created_at.strftime("%Y-%m-%d %H:%M")
            self.notify(f"Adding row: {user.id} | {user.name} | {created_str}")
            table.add_row(str(user.id), user.name, created_str, key=str(user.id))
        
        self.notify(f"Total rows in table: {table.row_count}")
        conn.close()


if __name__ == "__main__":
    app = DebugApp()
    app.run()
