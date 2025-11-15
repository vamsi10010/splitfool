"""Bill entry screen for creating new bills."""

from decimal import Decimal
from typing import Any

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, Select, Static

from splitfool.models.user import User
from splitfool.services.bill_service import AssignmentInput, BillInput, ItemInput
from splitfool.utils.errors import ValidationError


class ItemData:
    """Temporary storage for item being created."""

    def __init__(self) -> None:
        """Initialize empty item data."""
        self.description: str = ""
        self.cost: Decimal = Decimal("0")
        self.assignments: list[tuple[int, Decimal]] = []  # (user_id, fraction)


class BillEntryScreen(Screen[bool]):
    """Screen for entering bill details."""

    CSS = """
    BillEntryScreen {
        background: $surface;
    }
    
    #form-container {
        width: 100%;
        height: 100%;
        padding: 1;
    }
    
    #bill-section {
        width: 100%;
        height: auto;
        border: solid $primary;
        padding: 1;
        margin-bottom: 1;
    }
    
    #items-section {
        width: 100%;
        height: auto;
        border: solid $primary;
        padding: 1;
        margin-bottom: 1;
    }
    
    #preview-section {
        width: 100%;
        height: auto;
        border: solid $accent;
        padding: 1;
        margin-bottom: 1;
    }
    
    Label {
        width: 100%;
        margin-bottom: 1;
    }
    
    Input, Select {
        width: 100%;
        margin-bottom: 1;
    }
    
    Button {
        margin: 0 1;
    }
    
    .button-row {
        width: 100%;
        height: auto;
        align: center middle;
    }
    
    .item-button-row {
        width: 100%;
        height: auto;
        margin-bottom: 1;
    }
    
    .item-display-btn {
        width: 1fr;
        text-align: left;
    }
    
    .item-action-btn {
        width: auto;
        min-width: 10;
    }
    
    .error {
        color: $error;
        text-style: bold;
    }
    
    .success {
        color: $success;
        text-style: bold;
    }
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("ctrl+s", "save", "Save Bill"),
        ("ctrl+i", "add_item", "Add Item"),
        ("ctrl+p", "preview", "Preview"),
    ]

    def __init__(self, users: list[User]) -> None:
        """Initialize bill entry screen.

        Args:
            users: List of available users
        """
        super().__init__()
        self.users = users
        self.items: list[ItemData] = []
        self.current_item: ItemData | None = None

    def compose(self) -> ComposeResult:
        """Compose bill entry screen.

        Yields:
            Widgets for the screen
        """
        yield Header()

        with VerticalScroll(id="form-container"):
            # Bill details section
            with Container(id="bill-section"):
                yield Label("Bill Details", classes="section-title")
                yield Label("Description:")
                yield Input(placeholder="e.g., Dinner at restaurant", id="description")
                yield Label("Payer:")
                yield Select(
                    options=[(user.name, user.id) for user in self.users],
                    id="payer",
                    allow_blank=False,
                )
                yield Label("Tax/Tip/Fees:")
                yield Input(placeholder="0.00", id="tax")

            # Items section
            with Container(id="items-section"):
                yield Label("Items", classes="section-title")
                yield Static("No items added yet.", id="items-list")
                with Horizontal(classes="button-row"):
                    yield Button("Add Item", id="add-item-btn", variant="primary")

            # Preview section
            with Container(id="preview-section"):
                yield Label("Preview", classes="section-title")
                yield Static("Add items to see preview", id="preview-content")

            # Action buttons
            with Horizontal(classes="button-row"):
                yield Button("Save Bill", id="save-btn", variant="success")
                yield Button("Cancel", id="cancel-btn", variant="error")

        yield Footer()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press.

        Args:
            event: Button pressed event
        """
        button_id = str(event.button.id)

        if button_id == "add-item-btn":
            self.action_add_item()
        elif button_id == "save-btn":
            await self.action_save()
        elif button_id == "cancel-btn":
            await self.action_cancel()
        elif button_id.startswith("edit-"):
            # Extract item index and edit
            index = int(button_id.replace("edit-", ""))
            self.action_edit_item(index)
        elif button_id.startswith("delete-"):
            # Extract item index and delete
            index = int(button_id.replace("delete-", ""))
            await self.action_delete_item(index)

    def action_add_item(self) -> None:
        """Open item entry dialog."""
        from splitfool.ui.screens.item_entry import ItemEntryScreen

        def handle_item_result(item_data: ItemData | None) -> None:
            """Handle result from item entry screen."""
            if item_data:
                self.items.append(item_data)
                self.call_later(self.update_items_display)
                self.call_later(self.update_preview)

        self.app.push_screen(ItemEntryScreen(self.users), handle_item_result)

    def action_edit_item(self, index: int) -> None:
        """Edit an existing item.
        
        Args:
            index: Index of item to edit
        """
        from splitfool.ui.screens.item_entry import ItemEntryScreen

        if 0 <= index < len(self.items):
            existing_item = self.items[index]
            
            def handle_edit_result(item_data: ItemData | None) -> None:
                """Handle result from item edit screen."""
                if item_data:
                    self.items[index] = item_data
                    self.call_later(self.update_items_display)
                    self.call_later(self.update_preview)

            self.app.push_screen(
                ItemEntryScreen(self.users, existing_item=existing_item),
                handle_edit_result
            )

    async def action_delete_item(self, index: int) -> None:
        """Delete an item.
        
        Args:
            index: Index of item to delete
        """
        if 0 <= index < len(self.items):
            self.items.pop(index)
            await self.update_items_display()
            await self.update_preview()

    async def action_preview(self) -> None:
        """Update preview display."""
        await self.update_preview()

    async def action_save(self) -> None:
        """Save the bill."""
        try:
            # Validate and collect bill data
            description_input = self.query_one("#description", Input)
            payer_select = self.query_one("#payer", Select)
            tax_input = self.query_one("#tax", Input)

            description = description_input.value.strip()
            if not description:
                raise ValidationError("Description is required", code="BILL_DESC")

            if payer_select.value is None or payer_select.value == Select.BLANK:
                raise ValidationError("Payer is required", code="BILL_PAYER")

            payer_id = int(payer_select.value)  # type: ignore[arg-type]

            tax_str = tax_input.value.strip() or "0"
            try:
                tax = Decimal(tax_str)
                if tax < Decimal("0"):
                    raise ValidationError("Tax cannot be negative", code="BILL_TAX")
            except (ValueError, ArithmeticError) as e:
                raise ValidationError(f"Invalid tax amount: {tax_str}", code="BILL_TAX") from e

            if not self.items:
                raise ValidationError("At least one item is required", code="BILL_ITEMS")

            # Convert items to BillInput format
            item_inputs: list[ItemInput] = []
            for item in self.items:
                assignment_inputs = [
                    AssignmentInput(user_id=user_id, fraction=fraction)
                    for user_id, fraction in item.assignments
                ]
                item_inputs.append(
                    ItemInput(
                        description=item.description,
                        cost=item.cost,
                        assignments=assignment_inputs,
                    )
                )

            # Create bill input
            bill_input = BillInput(
                payer_id=payer_id,
                description=description,
                tax=tax,
                items=item_inputs,
            )

            # Save via service
            from splitfool.ui.app import SplitfoolApp
            app = self.app
            assert isinstance(app, SplitfoolApp), "App must be SplitfoolApp"
            assert app.bill_service is not None, "BillService must be initialized"
            
            app.bill_service.create_bill(bill_input)
            self.dismiss(True)

        except ValidationError as e:
            preview_content = self.query_one("#preview-content", Static)
            preview_content.update(f"[red]Error: {e.message}[/red]")
        except Exception as e:
            preview_content = self.query_one("#preview-content", Static)
            preview_content.update(f"[red]Unexpected error: {str(e)}[/red]")

    async def action_cancel(self) -> None:
        """Cancel bill entry."""
        self.dismiss(False)

    async def update_items_display(self) -> None:
        """Update the items list display."""
        items_container = self.query_one("#items-section", Container)
        
        # Remove old items display
        try:
            old_list = items_container.query_one("#items-list")
            await old_list.remove()
        except Exception:
            pass
        
        # Remove old item buttons
        for widget in items_container.query(".item-button-row"):
            await widget.remove()

        if not self.items:
            static = Static("No items added yet.", id="items-list")
            await items_container.mount(static, before="#add-item-btn")
            return

        # Create clickable item list
        for i, item in enumerate(self.items):
            user_count = len(item.assignments)
            item_text = (
                f"{i+1}. {item.description} - ${item.cost:.2f} "
                f"(split {user_count} way{'s' if user_count != 1 else ''})"
            )
            
            item_btn = Button(
                item_text, 
                id=f"item-{i}",
                classes="item-display-btn"
            )
            edit_btn = Button("Edit", id=f"edit-{i}", variant="warning", classes="item-action-btn")
            delete_btn = Button("Delete", id=f"delete-{i}", variant="error", classes="item-action-btn")
            
            item_row = Horizontal(item_btn, edit_btn, delete_btn, classes="item-button-row")
            await items_container.mount(item_row, before=0)

    async def update_preview(self) -> None:
        """Update the preview display."""
        preview_content = self.query_one("#preview-content", Static)

        if not self.items:
            preview_content.update("Add items to see preview")
            return

        # Calculate subtotal
        subtotal = sum(item.cost for item in self.items)

        # Get tax
        tax_input = self.query_one("#tax", Input)
        tax_str = tax_input.value.strip() or "0"
        try:
            tax = Decimal(tax_str)
        except (ValueError, ArithmeticError):
            tax = Decimal("0")

        total = subtotal + tax

        # Calculate user shares
        user_shares: dict[int, Decimal] = {}
        for item in self.items:
            for user_id, fraction in item.assignments:
                if user_id not in user_shares:
                    user_shares[user_id] = Decimal("0")
                user_shares[user_id] += item.cost * fraction

        # Add proportional tax
        if subtotal > Decimal("0"):
            for user_id in user_shares:
                tax_share = tax * (user_shares[user_id] / subtotal)
                user_shares[user_id] += tax_share

        # Build preview text
        lines = [
            f"Subtotal: ${subtotal:.2f}",
            f"Tax/Tip: ${tax:.2f}",
            f"Total: ${total:.2f}",
            "",
            "User Shares:",
        ]

        user_dict = {user.id: user.name for user in self.users}
        for user_id, amount in sorted(user_shares.items()):
            user_name = user_dict.get(user_id, f"User {user_id}")
            lines.append(f"  {user_name}: ${amount:.2f}")

        preview_content.update("\n".join(lines))

    async def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes for live preview.

        Args:
            event: Input changed event
        """
        if event.input.id == "tax":
            await self.update_preview()
