"""Confirmation dialog widget."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Static


class ConfirmationDialog(ModalScreen[bool]):
    """Modal dialog for confirming actions."""

    CSS = """
    ConfirmationDialog {
        align: center middle;
    }
    
    #dialog {
        width: 60;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 1;
    }
    
    #title {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }
    
    #message {
        width: 100%;
        margin-bottom: 1;
        padding: 1;
    }
    
    .button-row {
        width: 100%;
        height: auto;
        align: center middle;
    }
    
    Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("enter", "confirm", "Confirm"),
    ]

    def __init__(
        self,
        title: str,
        message: str,
        confirm_label: str = "Confirm",
        cancel_label: str = "Cancel",
    ) -> None:
        """Initialize confirmation dialog.

        Args:
            title: Dialog title
            message: Dialog message
            confirm_label: Label for confirm button
            cancel_label: Label for cancel button
        """
        super().__init__()
        self.dialog_title = title
        self.dialog_message = message
        self.confirm_label = confirm_label
        self.cancel_label = cancel_label

    def compose(self) -> ComposeResult:
        """Compose dialog.

        Yields:
            Dialog widgets
        """
        with Container(id="dialog"):
            yield Label(self.dialog_title, id="title")
            yield Static(self.dialog_message, id="message")
            with Horizontal(classes="button-row"):
                yield Button(
                    f"✅ {self.confirm_label} [enter]",
                    id="confirm-btn",
                    variant="success",
                )
                yield Button(
                    f"❌ {self.cancel_label} [esc]",
                    id="cancel-btn",
                    variant="error",
                )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses.

        Args:
            event: Button pressed event
        """
        if event.button.id == "confirm-btn":
            self.action_confirm()
        elif event.button.id == "cancel-btn":
            self.action_cancel()

    def action_confirm(self) -> None:
        """Confirm action."""
        self.dismiss(True)

    def action_cancel(self) -> None:
        """Cancel action."""
        self.dismiss(False)
