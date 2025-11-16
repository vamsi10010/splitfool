"""User management screen."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Button, DataTable, Input, Static

from splitfool.utils.errors import DuplicateUserError, ValidationError


class UserManagementScreen(Screen[None]):
    """Screen for managing users."""

    CSS = """
    UserManagementScreen {
        layout: vertical;
        padding: 1;
    }

    #title {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
        height: auto;
    }

    #user-list {
        height: 30;
        margin: 1 0;
        border: solid $primary;
    }

    #user-table {
        height: 100%;
        width: 100%;
    }

    #form-container {
        height: 10;
        border: solid $primary;
        padding: 1;
    }

    Input {
        width: 1fr;
        margin-right: 1;
    }

    Button {
        margin-right: 1;
    }

    #error-message {
        color: $error;
        margin-top: 1;
    }
    """

    BINDINGS = [
        ("n", "new_user", "New User"),
        ("e", "edit_user", "Edit User"),
        ("d", "delete_user", "Delete User"),
        ("escape", "go_back", "Back"),
    ]

    def __init__(self) -> None:
        """Initialize user management screen."""
        super().__init__()
        self.selected_user_id: int | None = None

    def compose(self) -> ComposeResult:
        """Compose user management screen.

        Yields:
            Screen widgets
        """
        yield Static("👥 User Management", id="title")

        with Container(id="user-list"):
            yield DataTable(id="user-table")

        with Container(id="form-container"):
            with Horizontal():
                yield Input(placeholder="Enter user name...", id="user-input")
                yield Button("Add [Enter]", id="btn-add", variant="primary")
                yield Button("Edit [e]", id="btn-edit", variant="default")
                yield Button("Delete [d]", id="btn-delete", variant="error")
            yield Static("", id="error-message")

    def on_mount(self) -> None:
        """Initialize screen on mount."""
        table = self.query_one("#user-table", DataTable)

        # Only add columns if they don't exist
        if not table.columns:
            table.add_columns("ID", "Name", "Created")

        # Set cursor and display options
        table.cursor_type = "row"
        table.zebra_stripes = True  # Alternate row colors for visibility
        table.show_cursor = True

        self.load_users()

        # Focus the table to ensure it's visible
        table.focus()

    def load_users(self) -> None:
        """Load users from database and populate table."""
        table = self.query_one("#user-table", DataTable)

        # Clear only rows, keeping columns
        table.clear(columns=False)

        from splitfool.ui.app import SplitfoolApp
        app = self.app
        assert isinstance(app, SplitfoolApp)

        if app.user_service:
            users = app.user_service.get_all_users()
            self.notify(f"Loading {len(users)} users...")
            for user in users:
                created_str = user.created_at.strftime("%Y-%m-%d %H:%M")
                table.add_row(str(user.id), user.name, created_str, key=str(user.id))

            # Force table to refresh and update display
            table.refresh()
            self.notify(f"✓ Loaded {table.row_count} rows")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses.

        Args:
            event: Button press event
        """
        if event.button.id == "btn-add":
            self.add_user()
        elif event.button.id == "btn-edit":
            self.action_edit_user()
        elif event.button.id == "btn-delete":
            self.action_delete_user()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission (Enter key).

        Args:
            event: Input submission event
        """
        self.add_user()

    def add_user(self) -> None:
        """Add a new user or update existing user if one is selected."""
        user_input = self.query_one("#user-input", Input)
        error_message = self.query_one("#error-message", Static)

        name = user_input.value.strip()

        if not name:
            error_message.update("⚠️ Please enter a user name")
            return

        from splitfool.ui.app import SplitfoolApp
        app = self.app
        assert isinstance(app, SplitfoolApp)

        try:
            if app.user_service:
                # If a user is selected, update it; otherwise create new
                if self.selected_user_id is not None:
                    app.user_service.update_user(self.selected_user_id, name)
                    user_input.value = ""
                    error_message.update("")
                    self.selected_user_id = None
                    self.load_users()
                    self.app.notify(f"✅ User updated to '{name}'")
                else:
                    app.user_service.create_user(name)
                    user_input.value = ""
                    error_message.update("")
                    self.load_users()
                    self.app.notify(f"✅ User '{name}' created")
        except ValidationError as e:
            error_message.update(f"⚠️ {e.message}")
        except DuplicateUserError as e:
            error_message.update(f"⚠️ {e.message}")

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection in table.

        Args:
            event: Row selection event
        """
        self.selected_user_id = int(str(event.row_key.value))

    def action_new_user(self) -> None:
        """Focus on input field for new user."""
        user_input = self.query_one("#user-input", Input)
        user_input.value = ""
        user_input.focus()

    def action_edit_user(self) -> None:
        """Edit the selected user."""
        error_message = self.query_one("#error-message", Static)
        user_input = self.query_one("#user-input", Input)

        if self.selected_user_id is None:
            error_message.update("⚠️ Please select a user to edit")
            return

        from splitfool.ui.app import SplitfoolApp
        app = self.app
        assert isinstance(app, SplitfoolApp)

        try:
            if app.user_service:
                user = app.user_service.get_user(self.selected_user_id)

                # Pre-fill the input with current name
                user_input.value = user.name
                user_input.focus()

                # Update button to show we're editing
                error_message.update(f"✏️ Editing: {user.name} (modify name and press Enter)")
        except Exception as e:
            error_message.update(f"⚠️ {str(e)}")

    def action_delete_user(self) -> None:
        """Delete the selected user with confirmation."""
        error_message = self.query_one("#error-message", Static)

        if self.selected_user_id is None:
            error_message.update("⚠️ Please select a user to delete")
            return

        from splitfool.ui.app import SplitfoolApp
        app = self.app
        assert isinstance(app, SplitfoolApp)

        try:
            if app.user_service:
                user = app.user_service.get_user(self.selected_user_id)

                # Show confirmation dialog
                def check_delete(confirmed: bool) -> None:
                    """Handle delete confirmation."""
                    if confirmed and app.user_service:
                        try:
                            app.user_service.delete_user(self.selected_user_id)  # type: ignore
                            error_message.update("")
                            self.selected_user_id = None
                            self.load_users()
                            self.app.notify(f"✅ User '{user.name}' deleted")
                        except Exception as e:
                            error_message.update(f"⚠️ {str(e)}")

                self.app.push_screen(
                    ConfirmDeleteScreen(user.name),
                    check_delete
                )
        except Exception as e:
            error_message.update(f"⚠️ {str(e)}")

    def action_go_back(self) -> None:
        """Go back to home screen."""
        self.app.pop_screen()


class ConfirmDeleteScreen(Screen[bool]):
    """Confirmation dialog for user deletion."""

    CSS = """
    ConfirmDeleteScreen {
        align: center middle;
    }

    #dialog {
        width: 50;
        height: auto;
        border: solid $error;
        background: $surface;
        padding: 2;
    }

    #message {
        width: 100%;
        text-align: center;
        margin-bottom: 2;
    }

    Button {
        width: 1fr;
        margin: 0 1;
    }
    """

    def __init__(self, user_name: str) -> None:
        """Initialize confirmation dialog.

        Args:
            user_name: Name of user to delete
        """
        super().__init__()
        self.user_name = user_name

    def compose(self) -> ComposeResult:
        """Compose confirmation dialog.

        Yields:
            Dialog widgets
        """
        with Container(id="dialog"):
            yield Static(
                f"⚠️ Delete user '{self.user_name}'?\n\nThis action cannot be undone.",
                id="message"
            )
            with Horizontal():
                yield Button("Cancel [Esc]", id="btn-cancel", variant="default")
                yield Button("Delete [Enter]", id="btn-confirm", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses.

        Args:
            event: Button press event
        """
        if event.button.id == "btn-confirm":
            self.dismiss(True)
        else:
            self.dismiss(False)

    def on_key(self, event: Button.Pressed) -> None:
        """Handle key presses.

        Args:
            event: Key press event
        """
        if event.key == "enter":
            self.dismiss(True)
        elif event.key == "escape":
            self.dismiss(False)
