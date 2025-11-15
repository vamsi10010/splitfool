"""Simplest possible table test."""

from textual.app import App, ComposeResult
from textual.widgets import DataTable, Header, Footer


class SimpleApp(App):
    """Simple table test."""

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable(id="test-table")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#test-table", DataTable)
        
        # Add columns
        table.add_columns("ID", "Name", "Value")
        
        # Add hardcoded rows
        table.add_row("1", "Alice", "100")
        table.add_row("2", "Bob", "200")
        table.add_row("3", "Charlie", "300")
        
        self.notify(f"Added {table.row_count} rows")


if __name__ == "__main__":
    app = SimpleApp()
    app.run()
