"""Help screen with comprehensive documentation."""

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Markdown

HELP_CONTENT = """
# 🧾 Splitfool Help

**Version 0.1.0** - Bill Splitting Application

---

## 📚 Table of Contents

1. [Quick Start](#quick-start)
2. [User Management](#user-management)
3. [Creating Bills](#creating-bills)
4. [Viewing Balances](#viewing-balances)
5. [Bill History](#bill-history)
6. [Keyboard Shortcuts](#keyboard-shortcuts)
7. [Tips & Tricks](#tips-tricks)

---

## 🚀 Quick Start {#quick-start}

Splitfool helps you split bills among multiple people. Here's the basic workflow:

1. **Add Users** - Create entries for people who participate in bill splitting
2. **Create Bills** - Enter bills with items and assign costs to users
3. **View Balances** - See who owes whom
4. **Settle Up** - Clear all balances when debts are paid
5. **Review History** - Check past bills anytime

---

## 👥 User Management {#user-management}

**Access**: Press `[u]` from home screen or select "Manage Users"

### Adding a User
1. Click "Add User" or press `Ctrl+N`
2. Enter the person's name
3. Press Enter to save

### Editing a User
1. Select the user from the list
2. Click "Edit" or press Enter
3. Modify the name
4. Press Enter to save

### Deleting a User
1. Select the user from the list
2. Click "Delete" or press Delete key
3. Confirm deletion

**Note**: You cannot delete users with outstanding balances.

---

## 💵 Creating Bills {#creating-bills}

**Access**: Press `[b]` from home screen or select "New Bill"

### Step 1: Bill Details
- **Description**: What's the bill for? (e.g., "Dinner at Pizza Place")
- **Payer**: Who paid the bill?
- **Tax/Tip/Fees**: Any additional charges (optional, default: $0.00)

### Step 2: Add Items
1. Click "Add Item" or press `Ctrl+I`
2. Enter item description (e.g., "Margherita Pizza")
3. Enter item cost (e.g., "15.99")
4. Assign users to this item:
   - Select users who share this item
   - Set fractions (e.g., 0.5 for 50%, 1.0 for 100%)
   - **Fractions must sum to 1.0** for each item
   - Default: Equal split among selected users

### Step 3: Preview & Save
- Review the calculated shares in the preview section
- Each user's share includes:
  - Their portion of assigned items
  - Proportional share of tax/tips based on their items
- Press `Ctrl+S` to save the bill
- Press `Esc` to cancel

### Example: $100 Dinner Bill
```
Items:
- Pizza ($60) → Alice: 50%, Bob: 50%
- Salad ($40) → Bob: 100%
Tax: $10

Calculations:
Alice: $60 × 0.5 = $30 + tax ($3) = $33
Bob: $60 × 0.5 + $40 = $70 + tax ($7) = $77
```

---

## ⚖️ Viewing Balances {#viewing-balances}

**Access**: Press `[v]` from home screen or select "View Balances"

### Understanding Balances
- Shows **net** balances (mutual debts are offset)
- Only displays positive amounts owed
- Updates automatically when bills are created

### Example
If Alice owes Bob $50 and Bob owes Alice $30:
- Display shows: "Alice owes Bob: $27.00"
- The $30 is subtracted from the $50

### Settling Balances
1. Click "Settle All" or press `[s]`
2. Review the confirmation dialog showing all balances
3. Confirm to clear all balances
4. **Note**: Bills remain in history for records

**When to Settle**: After you've transferred money in real life and want to reset the app.

---

## 📜 Bill History {#bill-history}

**Access**: Press `[h]` from home screen or select "View History"

### Viewing Bills
- Bills are listed chronologically (most recent first)
- Shows: Date, Description, Payer, Total

### Bill Details
1. Select any bill from the list
2. Press Enter to view full details:
   - All items with costs
   - User assignments and fractions
   - Calculated shares for each user
   - Tax/tip distribution
3. Press `[b]` or Esc to return to list

---

## ⌨️ Keyboard Shortcuts {#keyboard-shortcuts}

### Global Shortcuts (Work Everywhere)
- `F1` or `?` - Show this help screen
- `Esc` - Go back / Cancel
- `q` - Quit application
- `Tab` - Navigate between fields
- `Arrow Keys` - Move selection up/down/left/right
- `Enter` - Select / Confirm

### Home Screen
- `u` - Manage Users
- `b` - New Bill
- `v` - View Balances
- `h` - View History
- `?` - Help

### User Management
- `Ctrl+N` - Add new user
- `Enter` - Edit selected user
- `Delete` - Delete selected user
- `Esc` - Return to home

### Bill Entry
- `Ctrl+I` - Add item to bill
- `Ctrl+P` - Preview calculations
- `Ctrl+S` - Save bill
- `Esc` - Cancel bill entry

### Balance View
- `s` - Settle all balances
- `r` - Refresh balances
- `Esc` - Return to home

### History View
- `Enter` - View bill details
- `b` - Back to bill list (when in detail view)
- `r` - Refresh history
- `Esc` - Return to home

---

## 💡 Tips & Tricks {#tips-tricks}

### 1. Equal Splits Made Easy
When adding items, if you want an equal split:
- Select all users who share the item
- Leave fractions at default
- The system automatically divides evenly

### 2. Complex Splits
For unequal splits (e.g., someone ate more):
- Manually set fractions for each user
- Example: Alice 0.6, Bob 0.4 (Alice pays 60%)
- Always ensure fractions sum to exactly 1.0

### 3. Tax Distribution
Tax/tips are distributed **proportionally**:
- If you pay 30% of items, you pay 30% of tax
- This ensures fair distribution

### 4. Settlement Strategy
**Option A - Settle Often**: Clear balances after each bill is paid
**Option B - Settle Monthly**: Let balances accumulate, settle at month-end

Both work! Choose what fits your group's payment style.

### 5. Data Persistence
All data is saved automatically to `splitfool.db`:
- No manual save required
- Bills persist even after settlement
- Safe to close and reopen anytime

### 6. Checking Calculations
Use History view to verify any bill:
- See exact items and assignments
- Review calculated shares
- Confirm tax distribution

---

## 🆘 Troubleshooting

### "Cannot delete user with outstanding balances"
**Solution**: Settle balances first, then delete the user.

### "Fractions must sum to 1.0"
**Solution**: Check your fraction values for each item. They must add up to exactly 1.0.
- ✓ Correct: 0.5 + 0.5 = 1.0
- ✗ Wrong: 0.6 + 0.6 = 1.2

### "No users found"
**Solution**: Add at least one user before creating bills.

### "Tax cannot be negative"
**Solution**: Enter 0 or a positive number for tax/tips.

---

## 📝 About

**Splitfool** is a terminal-based bill splitting application designed for simplicity and efficiency.

**Features**:
- Manual bill entry with itemized costs
- Flexible user assignments with custom fractions
- Automatic tax distribution
- Net balance calculation (mutual debts offset)
- All-or-nothing settlement
- Complete bill history
- Data persistence across sessions

**Technology**: Built with Python and Textual framework

**License**: MIT (see LICENSE file)

---

Press `Esc` to return to the application.
"""


class HelpScreen(Screen[None]):
    """Comprehensive help screen."""

    CSS = """
    HelpScreen {
        background: $surface;
    }

    #help-container {
        width: 100%;
        height: 100%;
        padding: 1;
    }

    Markdown {
        width: 100%;
        height: 100%;
        background: $surface;
        color: $text;
        padding: 1;
    }
    """

    BINDINGS = [
        ("escape", "close", "Close Help"),
        ("q", "close", "Close Help"),
    ]

    def compose(self) -> ComposeResult:
        """Compose help screen.

        Yields:
            Screen widgets
        """
        yield Header()

        with VerticalScroll(id="help-container"):
            yield Markdown(HELP_CONTENT)

        yield Footer()

    def action_close(self) -> None:
        """Close help screen and return to previous screen."""
        self.dismiss()
