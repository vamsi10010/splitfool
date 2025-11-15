"""Item entry dialog for adding items to a bill."""

from decimal import Decimal

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Checkbox, Input, Label, Static

from splitfool.models.user import User
from splitfool.ui.screens.bill_entry import ItemData
from splitfool.utils.errors import ValidationError


class ItemEntryScreen(ModalScreen[ItemData | None]):
    """Modal screen for entering item details."""

    CSS = """
    ItemEntryScreen {
        align: center middle;
    }
    
    #dialog {
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
    
    Label {
        margin-bottom: 1;
    }
    
    Input {
        width: 100%;
        margin-bottom: 1;
    }
    
    .user-row {
        width: 100%;
        height: auto;
        margin-bottom: 1;
    }
    
    .user-checkbox {
        width: 1fr;
    }
    
    .fraction-input {
        width: 20;
        margin-left: 2;
    }
    
    Button {
        margin: 0 1;
    }
    
    .button-row {
        width: 100%;
        height: auto;
        align: center middle;
        margin-top: 1;
    }
    
    .error {
        color: $error;
        text-style: bold;
        margin-top: 1;
    }
    """

    def __init__(self, users: list[User], existing_item: ItemData | None = None) -> None:
        """Initialize item entry screen.

        Args:
            users: List of available users
            existing_item: Optional existing item data for editing
        """
        super().__init__()
        self.users = users
        self.existing_item = existing_item
        self.user_checkboxes: dict[int, Checkbox] = {}
        self.fraction_inputs: dict[int, Input] = {}

    def compose(self) -> ComposeResult:
        """Compose item entry dialog.

        Yields:
            Widgets for the dialog
        """
        with Container(id="dialog"):
            title_text = "Edit Item" if self.existing_item else "Add Item"
            yield Static(title_text, id="title")

            yield Label("Description:")
            description_value = self.existing_item.description if self.existing_item else ""
            yield Input(
                placeholder="e.g., Pizza", 
                id="item-description",
                value=description_value
            )

            yield Label("Cost:")
            cost_value = str(self.existing_item.cost) if self.existing_item else ""
            yield Input(
                placeholder="0.00", 
                id="item-cost",
                value=cost_value
            )

            yield Label("Assign to users:")
            yield Static(
                "(Select users and optionally enter custom fractions, or leave blank for equal split)",
                classes="help-text",
            )

            # User assignment section
            # Build existing assignments map for pre-filling
            existing_assignments: dict[int, Decimal] = {}
            if self.existing_item:
                existing_assignments = {
                    user_id: fraction 
                    for user_id, fraction in self.existing_item.assignments
                }
            
            with Vertical(id="users-section"):
                for user in self.users:
                    user_id_typed = user.id
                    assert user_id_typed is not None, "User ID must not be None"
                    
                    with Horizontal(classes="user-row"):
                        # Pre-check if user was assigned to this item
                        is_assigned = user_id_typed in existing_assignments
                        checkbox = Checkbox(
                            user.name, 
                            id=f"user-{user_id_typed}",
                            value=is_assigned
                        )
                        self.user_checkboxes[user_id_typed] = checkbox
                        yield checkbox

                        # Pre-fill fraction if user was assigned
                        fraction_value = ""
                        if user_id_typed in existing_assignments:
                            fraction_value = str(existing_assignments[user_id_typed])
                        
                        fraction_input = Input(
                            placeholder="auto",
                            id=f"fraction-{user_id_typed}",
                            classes="fraction-input",
                            value=fraction_value,
                            disabled=not is_assigned
                        )
                        self.fraction_inputs[user_id_typed] = fraction_input
                        yield fraction_input

            yield Static("", id="error-message", classes="error")

            with Horizontal(classes="button-row"):
                yield Button("Add Item", id="add-btn", variant="success")
                yield Button("Cancel", id="cancel-btn")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press.

        Args:
            event: Button pressed event
        """
        if event.button.id == "add-btn":
            await self.add_item()
        elif event.button.id == "cancel-btn":
            self.dismiss(None)

    @on(Checkbox.Changed)
    async def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        """Handle checkbox state change to enable/disable fraction inputs.

        Args:
            event: Checkbox changed event
        """
        # Extract user_id from checkbox id (format: "user-{id}")
        checkbox_id = str(event.checkbox.id)
        if checkbox_id.startswith("user-"):
            user_id_str = checkbox_id.replace("user-", "")
            try:
                user_id = int(user_id_str)
                if user_id in self.fraction_inputs:
                    fraction_input = self.fraction_inputs[user_id]
                    fraction_input.disabled = not event.value
            except ValueError:
                pass

    async def add_item(self) -> None:
        """Validate and add the item."""
        error_message = self.query_one("#error-message", Static)
        error_message.update("")

        try:
            # Get item description
            description_input = self.query_one("#item-description", Input)
            description = description_input.value.strip()
            if not description:
                raise ValidationError("Item description is required", code="ITEM_DESC")

            # Get item cost
            cost_input = self.query_one("#item-cost", Input)
            cost_str = cost_input.value.strip()
            if not cost_str:
                raise ValidationError("Item cost is required", code="ITEM_COST")

            try:
                cost = Decimal(cost_str)
                if cost <= Decimal("0"):
                    raise ValidationError("Item cost must be positive", code="ITEM_COST")
            except (ValueError, ArithmeticError) as e:
                raise ValidationError(f"Invalid cost: {cost_str}", code="ITEM_COST") from e

            # Get selected users and their fractions
            selected_users: list[tuple[int, Decimal | None]] = []
            for user_id, checkbox in self.user_checkboxes.items():
                if checkbox.value:
                    fraction_input = self.fraction_inputs[user_id]
                    fraction_str = fraction_input.value.strip()

                    if fraction_str and fraction_str != "auto":
                        try:
                            fraction = Decimal(fraction_str)
                            if not (Decimal("0") < fraction <= Decimal("1")):
                                raise ValidationError(
                                    f"Fraction for {checkbox.label} must be between 0 and 1",
                                    code="ASSIGN_RANGE",
                                )
                            selected_users.append((user_id, fraction))
                        except (ValueError, ArithmeticError) as e:
                            raise ValidationError(
                                f"Invalid fraction for {checkbox.label}: {fraction_str}",
                                code="ASSIGN_FRACTION",
                            ) from e
                    else:
                        selected_users.append((user_id, None))

            if not selected_users:
                raise ValidationError("At least one user must be selected", code="ASSIGN_NONE")

            # Calculate equal split if any fractions are None
            auto_count = sum(1 for _, frac in selected_users if frac is None)
            manual_total = sum(frac for _, frac in selected_users if frac is not None)

            if auto_count > 0:
                remaining = Decimal("1") - (manual_total or Decimal("0"))
                if remaining <= Decimal("0"):
                    raise ValidationError(
                        "Manual fractions sum to 1.0 or more, cannot auto-split",
                        code="ASSIGN_SUM",
                    )
                auto_fraction = remaining / auto_count

                # Replace None fractions with calculated equal split
                assignments: list[tuple[int, Decimal]] = [
                    (user_id, frac if frac is not None else auto_fraction)
                    for user_id, frac in selected_users
                ]
            else:
                # All fractions are manual, validate they sum to 1.0
                total = sum(frac for _, frac in selected_users if frac is not None)
                if abs(total - Decimal("1.0")) > Decimal("0.001"):
                    raise ValidationError(
                        f"Fractions must sum to 1.0 (currently {total})", code="ASSIGN_SUM"
                    )
                assignments = [(user_id, frac) for user_id, frac in selected_users if frac is not None]

            # Create item data
            item_data = ItemData()
            item_data.description = description
            item_data.cost = cost
            item_data.assignments = assignments

            self.dismiss(item_data)

        except ValidationError as e:
            error_message.update(e.message)
        except Exception as e:
            error_message.update(f"Unexpected error: {str(e)}")
