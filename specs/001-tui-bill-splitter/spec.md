# Feature Specification: Splitfool TUI Bill-Splitting Application

**Feature Branch**: `001-tui-bill-splitter`  
**Created**: 2025-11-15  
**Status**: Draft  
**Input**: User description: "Develop splitfool. Splitfool is a TUI application for splitting bills among multiple users. As a user, this is how I would use splitfool: I launch splitfool from the command line; I see a rich TUI interface with multiple options; I can add, modify, and delete users; I can view outstanding balances for each user; Users owe money to each other; I can clear/settle balances between users; I can open the TUI later and see my previous data (everything is saved in a local database); In the TUI, I can add a new bill; Bill entry is completely manual; When adding a bill, I can do the following: Add an item with cost, Assign the item to one or more users, Assign different fractions of the item to each assigned user (default to equal split), Add tax + other costs to the bill, Specify who paid the bill (one user), See total cost of the bill, See how much each user owes for the bill, Be able to modify items, assigned users, fractions, tax, payer before finalizing the bill; After adding the bill, the balances of all users are updated accordingly; I can view a history of all bills added, with details; The TUI is responsive and works well on different terminal sizes; The TUI has keyboard shortcuts for common actions; The TUI has a help section that explains how to use the application; The application is robust and handles invalid inputs gracefully."

## Clarifications

### Session 2025-11-15

- Q: Settlement workflow and integration with external payment tracking → A: Settlement is all-or-nothing only (no partial settlements). User workflow: (1) Submit multiple bills in Splitfool, (2) View balance summary showing all net debts, (3) Manually transfer these balances to external payment tracking app, (4) Settle all balances in Splitfool with single action to reset system to zero. Splitfool is used for bill splitting calculations only; actual payment tracking happens in separate external app.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - User Management (Priority: P1)

As a user, I need to manage the people who participate in bill splitting so that I can track who owes money to whom.

**Why this priority**: Without users, the entire application is non-functional. This is the foundational capability required before any bill splitting can occur.

**Independent Test**: Can be fully tested by launching the application, adding multiple users with names, modifying user details, deleting users, and verifying changes persist across application restarts. Delivers value by establishing the participant roster.

**Acceptance Scenarios**:

1. **Given** the application is launched for the first time, **When** I select "Add User" and enter a name, **Then** the user is created and appears in the user list
2. **Given** I have existing users, **When** I select "Modify User" and change a user's name, **Then** the updated name is saved and reflected throughout the application
3. **Given** I have existing users, **When** I select "Delete User", **Then** the user is removed from the system
4. **Given** I have added users, **When** I close and reopen the application, **Then** all previously added users are still present
5. **Given** I attempt to add a user with an empty name, **When** I submit the form, **Then** the application displays an error and does not create the user
6. **Given** I attempt to delete a user with outstanding balances, **When** I confirm deletion, **Then** the system displays an error message indicating the user cannot be deleted until all balances are settled

---

### User Story 2 - Bill Entry and Item Management (Priority: P2)

As a user, I need to manually enter bills with multiple items and assign costs to participants so that the application can calculate who owes what.

**Why this priority**: This is the core value proposition - splitting bills accurately. Without this, the application cannot fulfill its primary purpose.

**Independent Test**: Can be fully tested by creating a bill, adding multiple items with costs, assigning items to different users with custom fractions, adding tax, specifying a payer, and verifying calculated amounts before finalizing. Delivers value by accurately computing split costs.

**Acceptance Scenarios**:

1. **Given** I have existing users, **When** I select "Add New Bill", **Then** I am presented with a bill entry interface
2. **Given** I am entering a bill, **When** I add an item with a cost and assign it to one user, **Then** that user owes the full item cost
3. **Given** I am entering a bill, **When** I add an item and assign it to multiple users with equal split (default), **Then** each user owes an equal fraction of the item cost
4. **Given** I am entering a bill with assigned items, **When** I change the fraction assignments (e.g., 70/30 split), **Then** the owed amounts update accordingly
5. **Given** I have items totaling $100 and add $10 tax, **When** I view the bill total, **Then** the total shows $110
6. **Given** I have a bill with items assigned to users, **When** I add tax to the bill, **Then** the tax is distributed proportionally based on each user's share of the subtotal
7. **Given** I am entering a bill, **When** I specify which user paid the entire bill, **Then** that user is recorded as the payer
8. **Given** I am entering a bill, **When** I view the summary before finalizing, **Then** I see each user's owed amount and to whom they owe it
9. **Given** I am entering a bill, **When** I modify items, assignments, or tax before finalizing, **Then** all changes are reflected in the calculated amounts
10. **Given** I enter invalid data (negative costs, fractions not summing to 1), **When** I attempt to proceed, **Then** the application displays clear error messages
11. **Given** I have completed entering a bill, **When** I finalize the bill, **Then** the bill is saved and all user balances are updated

---

### User Story 3 - Balance Viewing and Settlement (Priority: P3)

As a user, I need to view a summary of all outstanding balances between users and settle all balances at once so that I can manually transfer the balance information to my external payment tracking app and then reset Splitfool to zero.

**Why this priority**: While important for tracking, this builds on the previous stories. Users can technically operate without viewing balances if they record them externally, making this slightly lower priority.

**Use Case Context**: User manages actual payments in a separate external app. Splitfool's role is to: (1) accurately calculate and display net balances after multiple bills, (2) provide a clear summary for manual data entry into the external payment app, (3) allow bulk settlement (all-or-nothing) to reset the system once balances are recorded externally. Splitfool does NOT track individual payments or partial settlements.

**Independent Test**: Can be fully tested by creating users, adding multiple bills, viewing the balance summary showing who owes whom, settling all balances with a single action, and verifying all balances are cleared to zero. Delivers value by providing clear debt tracking and bulk settlement for external payment management.

**Acceptance Scenarios**:

1. **Given** I have users with no bills entered, **When** I view balances, **Then** all balances show as zero
2. **Given** I have entered bills, **When** I view the balance summary, **Then** I see a complete list showing who owes whom and how much (net balances)
3. **Given** User A owes User B $50 and User B owes User A $30, **When** I view balances, **Then** the display shows the net result (User A owes User B $20)
4. **Given** I have outstanding balances, **When** I select "Settle All Balances", **Then** I see a confirmation prompt showing all current balances that will be cleared
5. **Given** I confirm "Settle All Balances", **When** the settlement completes, **Then** all user balances are reset to zero
6. **Given** I have settled all balances, **When** I close and reopen the application, **Then** all balances remain at zero (settlement persists)

---

### User Story 4 - Bill History and Details (Priority: P4)

As a user, I need to view a history of all bills entered with full details so that I can review past transactions and verify accuracy.

**Why this priority**: This is a supporting feature for auditing and verification. While valuable, users can function without it if they keep external records.

**Independent Test**: Can be fully tested by entering multiple bills, accessing the bill history view, selecting individual bills to see full details (items, assignments, costs, payer), and verifying all historical data is accurate. Delivers value by providing transparency and audit trail.

**Acceptance Scenarios**:

1. **Given** I have entered multiple bills, **When** I select "View History", **Then** I see a chronological list of all bills
2. **Given** I am viewing the bill history, **When** I select a specific bill, **Then** I see all details: items, costs, user assignments, fractions, tax, payer, and total
3. **Given** I am viewing bill details, **When** I review the calculations, **Then** I can verify the math is correct
4. **Given** I have no bills entered, **When** I select "View History", **Then** I see a message indicating no bills exist
5. **Given** I am viewing a bill from history, **When** I navigate back, **Then** I return to the history list

---

### User Story 5 - TUI Usability and Responsiveness (Priority: P5)

As a user, I need a responsive TUI with keyboard shortcuts and help documentation so that I can work efficiently across different terminal environments.

**Why this priority**: While important for user experience, this is polish that can be added incrementally. Core functionality can work with basic navigation first.

**Independent Test**: Can be fully tested by resizing the terminal to different dimensions, using keyboard shortcuts for navigation and actions, accessing the help section, and verifying the interface remains functional and readable. Delivers value through improved efficiency and accessibility.

**Acceptance Scenarios**:

1. **Given** I launch the application in a standard terminal (80x24), **When** the interface renders, **Then** all elements are visible and properly formatted
2. **Given** I launch the application in a large terminal (200x50), **When** the interface renders, **Then** the layout adapts and uses available space effectively
3. **Given** I launch the application in a small terminal (40x10), **When** the interface renders, **Then** critical elements remain visible and usable (possibly with scrolling)
4. **Given** I am using the application, **When** I press designated keyboard shortcuts (e.g., Ctrl+N for new bill), **Then** the corresponding action is executed
5. **Given** I am anywhere in the application, **When** I press the help key (e.g., F1 or ?), **Then** I see context-sensitive help or a general help screen
6. **Given** I am viewing the help section, **When** I review the content, **Then** I see clear explanations of all features, navigation, and keyboard shortcuts
7. **Given** I am in any input field, **When** I press Esc or a cancel shortcut, **Then** I return to the previous screen without saving changes

---

### Edge Cases

- What happens when a user tries to add a bill with no users in the system?
- What happens when a user assigns an item to zero users?
- What happens when fractions assigned to an item don't sum to 1.0 (e.g., 0.3 + 0.3)?
- What happens when costs are entered with more than 2 decimal places (e.g., $10.999)?
- What happens when the terminal is resized while the application is running?
- What happens if the local database file is corrupted or missing on startup?
- What happens when a user enters extremely large cost values (e.g., $1,000,000,000)?
- What happens when a user tries to settle all balances when all balances are already zero?
- What happens when a user tries to delete themselves from a bill they paid?
- What happens when navigating with keyboard shortcuts and input focus is in a text field?
- What happens when two users have circular debts (A owes B, B owes C, C owes A)?

## Requirements *(mandatory)*

### Functional Requirements

#### User Management
- **FR-001**: System MUST allow users to create new users with a unique name
- **FR-002**: System MUST allow users to modify existing user names
- **FR-003**: System MUST allow users to delete users from the system
- **FR-004**: System MUST prevent deletion of users who have outstanding balances (either owed to them or owed by them)
- **FR-005**: System MUST persist all user data to local storage
- **FR-006**: System MUST prevent creation of users with empty or whitespace-only names
- **FR-007**: System MUST validate that user names are unique within the system

#### Bill Entry and Management
- **FR-008**: System MUST allow users to create new bills with a manual entry interface
- **FR-009**: System MUST allow adding multiple items to a bill, each with a description and cost
- **FR-010**: System MUST allow assigning each item to one or more users
- **FR-011**: System MUST default to equal split when multiple users are assigned to an item
- **FR-012**: System MUST allow custom fraction assignment for each user on an item (e.g., 0.6, 0.4)
- **FR-013**: System MUST validate that fractions assigned to an item sum to 1.0 (within a reasonable tolerance for floating-point precision)
- **FR-014**: System MUST allow adding tax and other additional costs to a bill
- **FR-015**: System MUST distribute tax proportionally based on each user's share of the pre-tax subtotal
- **FR-016**: System MUST allow specifying exactly one user as the payer of the bill
- **FR-017**: System MUST calculate and display the total cost of a bill (items + tax + other costs)
- **FR-018**: System MUST calculate and display how much each user owes based on their assigned items and tax share
- **FR-019**: System MUST allow modifying items, assignments, fractions, tax, and payer before finalizing a bill
- **FR-020**: System MUST update all user balances when a bill is finalized
- **FR-021**: System MUST persist all bill data to local storage
- **FR-022**: System MUST handle negative costs by displaying an error and preventing bill creation
- **FR-023**: System MUST round currency values to 2 decimal places for display

#### Balance Management
- **FR-024**: System MUST calculate and display outstanding balances for each user
- **FR-025**: System MUST display balances in a net format (simplifying mutual debts between users)
- **FR-026**: System MUST provide a single "Settle All Balances" action that clears all outstanding balances
- **FR-027**: System MUST display a confirmation summary showing all current balances before settling
- **FR-028**: System MUST reset all user balances to zero when "Settle All Balances" is confirmed
- **FR-029**: System MUST persist settlement actions to local storage

#### Bill History
- **FR-030**: System MUST display a chronological list of all bills entered
- **FR-031**: System MUST allow users to view detailed information for any historical bill
- **FR-032**: System MUST display all bill details including items, costs, assignments, fractions, tax, payer, and total
- **FR-033**: System MUST indicate when no bills have been entered

#### Data Persistence
- **FR-034**: System MUST store all data in a local database file
- **FR-035**: System MUST load all existing data when the application launches
- **FR-036**: System MUST handle missing database files by initializing a new empty database
- **FR-037**: System MUST handle corrupted database files by notifying the user and offering to reinitialize

#### TUI Interface
- **FR-038**: System MUST provide a text-based user interface (TUI) with multiple navigation options
- **FR-039**: System MUST render properly on terminals with dimensions of at least 80x24 characters
- **FR-040**: System MUST adapt layout to different terminal sizes (larger and smaller than 80x24)
- **FR-041**: System MUST provide keyboard shortcuts for common actions (new bill, add user, view balances, etc.)
- **FR-042**: System MUST provide a help section accessible from any screen
- **FR-043**: System MUST document all features, navigation controls, and keyboard shortcuts in the help section
- **FR-044**: System MUST handle terminal resize events and adjust the display accordingly
- **FR-045**: System MUST provide clear navigation cues (menus, prompts, status bars)
- **FR-046**: System MUST support canceling operations (e.g., Esc key) to return to the previous screen

#### Error Handling and Validation
- **FR-047**: System MUST display clear, user-friendly error messages for all invalid inputs
- **FR-048**: System MUST validate all numeric inputs to ensure they are positive numbers (except for settlements)
- **FR-049**: System MUST prevent finalizing a bill with no items
- **FR-050**: System MUST prevent finalizing a bill with no users assigned to any item
- **FR-051**: System MUST prevent creating a bill when no users exist in the system

### Key Entities

- **User**: Represents a person participating in bill splitting. Has a unique name. Participates in bills either as a payer or as someone assigned to items. Has calculated balance relationships with other users.

- **Bill**: Represents a single expense event. Contains multiple line items, tax/fees, a designated payer, and a timestamp. Links to users through item assignments.

- **Item**: Represents a single line item within a bill. Has a description and cost. Can be assigned to one or more users with specified fractions indicating each user's share.

- **Assignment**: Represents the relationship between an item and a user. Specifies the fraction (portion) of the item's cost that the user is responsible for. Multiple assignments can exist for a single item.

- **Balance**: Represents the net amount one user owes to another user. Calculated from all bills where one user paid and another user had assigned items. Can be positive (owed) or negative (to be received).

- **Settlement**: Represents a bulk action that resets all balances to zero. Records the timestamp when all balances were cleared. Used to sync with external payment tracking systems.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can launch the application and create their first user in under 30 seconds
- **SC-002**: Users can enter a complete bill with 5 items, assign them to 3 users, add tax, and finalize in under 3 minutes
- **SC-003**: Users can view their balance summary in under 5 seconds from any screen
- **SC-004**: Application starts and loads all existing data in under 2 seconds
- **SC-005**: Interface remains responsive (renders within 100ms) when resizing terminal between 40x10 and 200x50 dimensions
- **SC-006**: 95% of common user actions can be completed using keyboard shortcuts without mouse/touch interaction
- **SC-007**: Users can understand how to perform basic tasks (add user, add bill, view balances) within 2 minutes using the help section
- **SC-008**: Application handles 100+ users, 1000+ bills, and 10,000+ items without performance degradation (operations complete within stated time limits)
- **SC-009**: Zero data loss occurs when application is closed and reopened (100% data persistence)
- **SC-010**: Balance calculations are accurate to within 1 cent (±$0.01) due to rounding, validated against manual calculations
- **SC-011**: 100% of invalid inputs are caught and result in clear error messages rather than crashes or undefined behavior
- **SC-012**: Application recovers gracefully from 100% of corrupted database scenarios by notifying user and offering recovery options

## Assumptions

- The application is intended for personal or small group use (up to 100 users)
- All users using the application have access to the same device/database (not a multi-user networked system)
- Currency is assumed to be in a single denomination (e.g., USD); no multi-currency support required
- Terminal supports standard ANSI escape codes for colors and cursor positioning
- Users have basic familiarity with command-line applications and keyboard navigation
- Local database storage is sufficient; cloud sync or backup is not required
- Bills are entered after the fact (not during the meal/shopping); no real-time collaboration needed
- Timestamps use the system local time; no timezone conversion required
- The payer always pays the full bill amount (no split payment scenarios)
- Tax and other costs are flat amounts added to the bill, not percentages (though the system could accept pre-calculated percentage amounts)
- Users manage actual payments outside the application in a separate payment tracking system; Splitfool calculates and displays net balances only, with users manually transferring balance data to their external payment app before performing all-or-nothing settlement in Splitfool
- Settlement is an all-or-nothing operation; individual balance adjustments between specific users are not supported (by design, to maintain workflow compatibility with external payment tracking apps)

## Dependencies

- A TUI framework/library for building the text-based interface (user must select appropriate tooling)
- A local database system for persistence (user must select appropriate tooling)
- Standard terminal capabilities (ANSI escape codes, keyboard input)
- Operating system support for file I/O and database storage

## Out of Scope

- Web or mobile GUI interface
- Multi-device synchronization
- Cloud storage or backups
- Multi-currency support
- Percentage-based tax calculation (users must calculate tax amount manually)
- Receipt scanning or OCR
- Integration with payment platforms (Venmo, PayPal, etc.)
- Payment tracking or recording individual payments between users (handled by external payment tracking app)
- Partial settlement or individual balance adjustments between specific users (all-or-nothing settlement only)
- Email or SMS notifications
- Export to formats other than what the database provides
- User authentication or access control (single-user application)
- Undo/redo functionality for completed bills
- Recurring bills or templates
- Categories or tagging for bills
- Reporting or analytics beyond basic balance viewing
