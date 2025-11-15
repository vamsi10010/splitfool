"""Quick test to verify table display works."""

from textual.app import App, ComposeResult
from textual.widgets import DataTable, Header, Footer
from textual.containers import Container


class TestApp(App):
    """Test app for table display."""

    def compose(self) -> ComposeResult:
        """Compose app layout."""
        yield Header()
        yield Container(
            DataTable(id="test-table")
        )
        yield Footer()

    def on_mount(self) -> None:
        """Initialize on mount."""
        table = self.query_one("#test-table", DataTable)
        
        # Add columns
        table.add_columns("ID", "Name", "Value")
        
        # Add some test data
        table.add_row("1", "Test1", "Value1")
        table.add_row("2", "Test2", "Value2")
        table.add_row("3", "Test3", "Value3")
        
        self.notify("Added 3 rows to table")


if __name__ == "__main__":
    app = TestApp()
    app.run()
