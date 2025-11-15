# Implementation Tasks: Splitfool TUI Bill-Splitting Application

**Feature**: 001-tui-bill-splitter  
**Branch**: `001-tui-bill-splitter`  
**Generated**: 2025-11-15

## Overview

This document provides a complete task breakdown for implementing Splitfool, a TUI application for splitting bills among multiple users. Tasks are organized by user story to enable independent, incremental delivery.

**Key Principles**:
- Each user story phase is independently testable
- Tasks marked [P] can be executed in parallel with other [P] tasks
- MVP = Phase 1 (Setup) + Phase 2 (Foundational) + Phase 3 (User Story 1)
- Follow constitution standards: type hints, frozen dataclasses, Decimal for currency, 80%+ test coverage

---

## Implementation Strategy

### MVP Scope (First Deliverable)
**Phases 1-3**: Setup + Foundational + User Story 1 (User Management)

**Why**: User Story 1 provides immediate value (manage participants) and is required before any bill splitting can occur. It's independently testable and allows validation of the full stack (models → repositories → services → TUI).

**Estimated Time**: 3-5 days
**Deliverable**: Working TUI app where users can add/modify/delete participants with full data persistence.

### Incremental Delivery
After MVP, each user story phase can be delivered independently:
- **Phase 4 (US2)**: Bill entry and calculations - 5-7 days
- **Phase 5 (US3)**: Balance viewing and settlement - 3-4 days  
- **Phase 6 (US4)**: Bill history - 2-3 days
- **Phase 7 (US5)**: TUI polish and responsiveness - 2-3 days

**Total Estimated Time**: 2-3 weeks for complete feature

---

## Phase 1: Setup & Project Initialization

**Goal**: Establish project structure, dependencies, and development environment.

**Deliverable**: Executable project skeleton with passing tests and linting.

### Tasks

- [x] T001 Initialize uv project with pyproject.toml per plan.md (Python 3.11+)
- [x] T002 [P] Add dependencies to pyproject.toml: textual, pytest, pytest-cov, mypy, ruff
- [x] T003 [P] Create project directory structure in splitfool/ per plan.md
- [x] T004 [P] Create test directory structure in tests/ (unit/, integration/, fixtures/)
- [x] T005 [P] Create .gitignore file (exclude .venv/, __pycache__/, *.pyc, splitfool.db, .coverage, htmlcov/)
- [x] T006 [P] Create splitfool/__init__.py with version string
- [x] T007 [P] Create splitfool/__main__.py entry point (placeholder that prints "Splitfool v0.1.0")
- [x] T008 [P] Create README.md with project description and setup instructions
- [x] T009 Configure mypy in pyproject.toml with --strict mode
- [x] T010 Configure ruff in pyproject.toml for linting and formatting
- [x] T011 Configure pytest in pyproject.toml with coverage settings (target: 80%+)
- [x] T012 Verify setup: run `uv sync`, `uv run pytest`, `uv run mypy splitfool`, `uv run ruff check`

**Acceptance**: Project initializes, dependencies install, empty test suite passes, type checking passes, linting passes.

---

## Phase 2: Foundational Infrastructure

**Goal**: Implement core infrastructure needed by all user stories (database, models, utilities).

**Deliverable**: Working database layer with all entities, currency utilities, and error handling.

**Dependencies**: Requires Phase 1 completion.

### Tasks

#### Utilities & Error Handling

- [x] T013 [P] Implement custom exception classes in splitfool/utils/errors.py (SplitfoolError, ValidationError, UserNotFoundError, BillNotFoundError, DuplicateUserError, UserHasBalancesError)
- [x] T014 [P] Implement currency utilities in splitfool/utils/currency.py (setup Decimal context, format_currency(), parse_currency())
- [x] T015 [P] Implement validation utilities in splitfool/services/validation.py (validate_user_name(), validate_bill_fractions(), validate_positive_decimal())
- [x] T016 [P] Create splitfool/config.py with database path configuration and default settings

#### Data Models

- [x] T017 [P] Implement User model in splitfool/models/user.py (frozen dataclass with validation)
- [x] T018 [P] Implement Bill model in splitfool/models/bill.py (frozen dataclass with validation)
- [x] T019 [P] Implement Item model in splitfool/models/item.py (frozen dataclass with validation)
- [x] T020 [P] Implement Assignment model in splitfool/models/assignment.py (frozen dataclass with validation)
- [x] T021 [P] Implement Balance model in splitfool/models/balance.py (frozen dataclass, derived entity)
- [x] T022 [P] Implement Settlement model in splitfool/models/settlement.py (frozen dataclass)
- [x] T023 Create splitfool/models/__init__.py exposing all models

#### Database Layer

- [x] T024 Implement database schema in splitfool/db/schema.py (complete SQL DDL for all tables with indexes)
- [x] T025 Implement database connection management in splitfool/db/connection.py (get_connection(), initialize_database())
- [x] T026 Implement database initialization script (creates schema if not exists, handles migrations)
- [x] T027 [P] Implement UserRepository in splitfool/db/repositories/user_repository.py (create, get, get_all, update, delete, exists_by_name)
- [x] T028 [P] Implement BillRepository in splitfool/db/repositories/bill_repository.py (create, get, get_all with pagination, get_by_user, get_since_date)
- [x] T029 [P] Implement ItemRepository (placeholder for Phase 4, basic structure only)
- [x] T030 [P] Implement AssignmentRepository (placeholder for Phase 4, basic structure only)
- [x] T031 [P] Implement SettlementRepository in splitfool/db/repositories/settlement_repository.py (create, get_latest, get_all)
- [x] T032 Create splitfool/db/repositories/__init__.py exposing all repositories

#### Unit Tests for Foundation

- [x] T033 [P] Write unit tests for currency utilities in tests/unit/test_currency.py (Decimal precision, format/parse roundtrip)
- [x] T034 [P] Write unit tests for validation utilities in tests/unit/test_validation.py (all validation functions with edge cases)
- [x] T035 [P] Write unit tests for error classes in tests/unit/test_errors.py (error codes, messages)
- [x] T036 [P] Write unit tests for all models in tests/unit/test_models.py (validation, immutability, __post_init__ errors)
- [x] T037 [P] Write integration tests for database schema in tests/integration/test_schema.py (schema creation, constraints)
- [x] T038 [P] Write integration tests for UserRepository in tests/integration/test_repositories.py (CRUD operations with in-memory database)

**Acceptance**: All models created, database schema initializes successfully, repositories perform CRUD operations, tests pass with 90%+ coverage for foundational code.

---

## Phase 3: User Story 1 - User Management (Priority: P1)

**Goal**: Implement complete user management functionality with TUI.

**User Story**: As a user, I need to manage the people who participate in bill splitting so that I can track who owes money to whom.

**Independent Test**: Launch app, add multiple users with names, modify user details, delete users, verify persistence across restarts.

**Dependencies**: Requires Phase 2 completion.

### Tasks

#### Service Layer

- [x] T039 [US1] Implement UserService in splitfool/services/user_service.py (create_user, get_user, get_all_users, update_user, delete_user, user_has_balances)
- [x] T040 [US1] Implement business logic for user deletion with balance checking (calls BalanceService.user_has_outstanding_balances - stub for now)

#### TUI Components

- [x] T041 [US1] Implement basic Textual App skeleton in splitfool/ui/app.py (SplitfoolApp class with config, service injection)
- [x] T042 [US1] Implement HomeScreen in splitfool/ui/screens/home.py (menu with "Manage Users" option, keyboard shortcuts)
- [x] T043 [US1] Implement UserManagementScreen in splitfool/ui/screens/user_management.py (list users, add/edit/delete actions)
- [x] T044 [US1] Implement UserList widget in splitfool/ui/widgets/user_list.py (displays users in table format with reactive updates)
- [x] T045 [US1] Implement UserForm widget for add/edit operations (input validation, error display)
- [x] T046 [US1] Implement delete confirmation dialog for users
- [x] T047 [US1] Wire up keyboard shortcuts for user management (Ctrl+N for new user, Enter to edit, Delete key)

#### Integration & Testing

- [x] T048 [US1] Write unit tests for UserService in tests/unit/test_services.py (all CRUD operations, validation errors, balance checking)
- [x] T049 [US1] Write integration test for complete user management workflow in tests/integration/test_user_workflow.py (add → modify → delete → persistence)
- [ ] T050 [US1] Write TUI tests for UserManagementScreen using Textual pilot mode (navigation, form submission, error handling)

#### Entry Point

- [x] T051 [US1] Update splitfool/__main__.py to launch SplitfoolApp with database initialization
- [x] T052 [US1] Add CLI argument parsing for --db-path option

**Acceptance Criteria**:
1. ✅ User can launch app and see home screen
2. ✅ User can navigate to user management screen
3. ✅ User can add a new user with validation (empty name rejected)
4. ✅ User can modify existing user's name (duplicate name rejected)
5. ✅ User can delete user (blocked if has balances - stub check passes for now)
6. ✅ All user data persists across app restarts
7. ✅ Test coverage ≥ 85% for user management code
8. ✅ All type checks pass, no linting errors

**MVP Checkpoint**: After Phase 3, you have a working TUI app with full user management!

---

## Phase 4: User Story 2 - Bill Entry and Item Management (Priority: P2)

**Goal**: Implement bill entry with items, assignments, tax, and split calculations.

**User Story**: As a user, I need to manually enter bills with multiple items and assign costs to participants so that the application can calculate who owes what.

**Independent Test**: Create a bill with multiple items, assign to different users with custom fractions, add tax, specify payer, verify calculations, finalize and verify persistence.

**Dependencies**: Requires Phase 3 completion (needs users to exist).

### Tasks

#### Complete Item & Assignment Repositories

- [x] T053 [US2] Complete ItemRepository in splitfool/db/repositories/item_repository.py (create, get_by_bill, delete, update)
- [x] T054 [US2] Complete AssignmentRepository in splitfool/db/repositories/assignment_repository.py (create, get_by_item, get_by_user, delete, validate_fractions_sum)

#### Service Layer - Bill Creation

- [x] T055 [US2] Implement BillService.create_bill() in splitfool/services/bill_service.py (validates input, creates bill + items + assignments in transaction)
- [x] T056 [US2] Implement BillService.calculate_user_share() (calculates item costs + proportional tax for a user)
- [x] T057 [US2] Implement BillService.calculate_total_cost() (sums all items + tax)
- [x] T058 [US2] Implement BillService.preview_bill() (shows what each user would owe without saving)
- [x] T059 [US2] Implement BillService.get_bill() (retrieves bill with all items and assignments)
- [x] T060 [US2] Implement bill validation logic (payer exists, fractions sum to 1.0, at least one item, etc.)

#### TUI Components - Bill Entry

- [x] T061 [US2] Implement BillEntryScreen in splitfool/ui/screens/bill_entry.py (main workflow orchestrator)
- [x] T062 [US2] Implement BillForm widget in splitfool/ui/widgets/bill_form.py (description, payer selection, tax input)
- [x] T063 [US2] Implement ItemList widget (displays items being added to bill with edit/delete options)
- [x] T064 [US2] Implement ItemForm widget (add/edit item with description and cost)
- [x] T065 [US2] Implement AssignmentForm widget (assign users to item with fraction inputs, default equal split)
- [x] T066 [US2] Implement BillSummaryWidget (real-time preview showing each user's owed amount)
- [x] T067 [US2] Implement bill finalization confirmation dialog (shows calculated splits before saving)
- [x] T068 [US2] Add "New Bill" option to HomeScreen with keyboard shortcut (Ctrl+B)

#### Validation & Error Handling

- [ ] T069 [US2] Implement comprehensive input validation for bill entry (positive costs, valid fractions, non-empty descriptions)
- [ ] T070 [US2] Implement error display widgets for validation failures (clear, actionable messages with error codes)
- [ ] T071 [US2] Handle edge case: attempt to create bill when no users exist (display helpful error)

#### Integration & Testing

- [ ] T072 [US2] Write unit tests for BillService in tests/unit/test_services.py (create_bill, calculate_user_share, calculate_total_cost, preview_bill)
- [ ] T073 [US2] Write unit tests for bill validation logic (all validation rules with edge cases)
- [ ] T074 [US2] Write integration test for complete bill workflow in tests/integration/test_bill_workflow.py (create bill with multiple items, various fraction splits, tax distribution)
- [ ] T075 [US2] Write integration test for complex bill scenarios (equal split, custom fractions, single user items, tax distribution accuracy)
- [ ] T076 [US2] Write TUI tests for BillEntryScreen using pilot mode (add items, modify assignments, preview, finalize)

**Acceptance Criteria**:
1. ✅ User can navigate to bill entry screen
2. ✅ User can add multiple items with costs
3. ✅ User can assign items to one or more users
4. ✅ User can specify custom fractions for each user (default equal split works)
5. ✅ User can add tax and see it distributed proportionally
6. ✅ User can specify which user paid the bill
7. ✅ User sees real-time preview of what each user owes
8. ✅ User can modify items/assignments before finalizing
9. ✅ Bill saves successfully and data persists
10. ✅ Validation catches all invalid inputs (negative costs, fractions ≠ 1.0)
11. ✅ Test coverage ≥ 85% for bill management code
12. ✅ Currency calculations accurate to ±$0.01

---

## Phase 5: User Story 3 - Balance Viewing and Settlement (Priority: P3)

**Goal**: Implement balance calculation, viewing, and all-or-nothing settlement.

**User Story**: As a user, I need to view a summary of all outstanding balances between users and settle all balances at once so that I can manually transfer the balance information to my external payment tracking app and then reset Splitfool to zero.

**Independent Test**: Create users, add multiple bills, view balance summary showing net debts, settle all balances, verify all balances are zero and settlement persists.

**Dependencies**: Requires Phase 4 completion (needs bills to exist).

### Tasks

#### Service Layer - Balance Calculation

- [ ] T077 [US3] Implement BalanceService.get_all_balances() in splitfool/services/balance_service.py (calculates net balances from all bills since last settlement)
- [ ] T078 [US3] Implement balance calculation algorithm (aggregate debts, net out mutual debts, return only positive balances)
- [ ] T079 [US3] Implement BalanceService.get_user_balances() (returns debts and credits for specific user)
- [ ] T080 [US3] Implement BalanceService.user_has_outstanding_balances() (used by user deletion check)
- [ ] T081 [US3] Implement BalanceService.preview_settlement() (shows current balances that would be cleared)
- [ ] T082 [US3] Implement BalanceService.settle_all_balances() (creates settlement record with timestamp and optional note)
- [ ] T083 [US3] Implement BalanceService.get_last_settlement() (retrieves most recent settlement for balance calculation cutoff)

#### TUI Components - Balance Viewing

- [ ] T084 [US3] Implement BalanceViewScreen in splitfool/ui/screens/balance_view.py (displays net balances, settlement button)
- [ ] T085 [US3] Implement BalanceTable widget in splitfool/ui/widgets/balance_table.py (displays "X owes Y: $Z" for all non-zero balances)
- [ ] T086 [US3] Implement settlement confirmation dialog (shows all current balances with "Are you sure?" confirmation)
- [ ] T087 [US3] Implement settlement success notification (confirms all balances cleared)
- [ ] T088 [US3] Add "View Balances" option to HomeScreen with keyboard shortcut (Ctrl+V)
- [ ] T089 [US3] Handle edge case: display "All balances settled" when no outstanding debts exist

#### Integration & Testing

- [ ] T090 [US3] Write unit tests for BalanceService in tests/unit/test_services.py (get_all_balances, settlement operations)
- [ ] T091 [US3] Write unit tests for balance calculation algorithm (netting mutual debts, multiple users, edge cases)
- [ ] T092 [US3] Write integration test for balance calculation in tests/integration/test_balance_calculation.py (verify accuracy with complex bill scenarios)
- [ ] T093 [US3] Write integration test for settlement workflow (settle → verify zero → verify persistence → verify bills still exist in history)
- [ ] T094 [US3] Write TUI tests for BalanceViewScreen using pilot mode (view balances, settle with confirmation)

#### Update User Deletion Check

- [ ] T095 [US3] Update UserService.delete_user() to call BalanceService.user_has_outstanding_balances() (replace stub from Phase 3)

**Acceptance Criteria**:
1. ✅ User can navigate to balance view screen
2. ✅ User sees net balances (mutual debts netted out correctly)
3. ✅ User sees "All balances settled" when no debts exist
4. ✅ User can initiate "Settle All Balances" action
5. ✅ User sees confirmation dialog showing all balances before settling
6. ✅ After settlement, all balances show as zero
7. ✅ Settlement persists across app restarts
8. ✅ Bills remain in history after settlement
9. ✅ User deletion blocked when user has outstanding balances (now fully functional)
10. ✅ Test coverage ≥ 85% for balance management code
11. ✅ Balance calculations mathematically accurate

---

## Phase 6: User Story 4 - Bill History and Details (Priority: P4)

**Goal**: Implement bill history viewing with detailed drill-down.

**User Story**: As a user, I need to view a history of all bills entered with full details so that I can review past transactions and verify accuracy.

**Independent Test**: Enter multiple bills, access bill history view, select individual bills to see full details, verify all data accurate.

**Dependencies**: Requires Phase 4 completion (needs bills to exist).

### Tasks

#### Service Layer - History

- [ ] T096 [US4] Implement BillService.get_all_bills() with pagination (retrieves bills in chronological order, most recent first)
- [ ] T097 [US4] Implement BillService.get_bill_detail() (retrieves complete bill with items, assignments, payer name, calculated shares)

#### TUI Components - History

- [ ] T098 [US4] Implement HistoryScreen in splitfool/ui/screens/history.py (lists all bills with summary info)
- [ ] T099 [US4] Implement BillListWidget (displays bills in chronological order with pagination controls)
- [ ] T100 [US4] Implement BillDetailWidget (displays complete bill information: items, costs, assignments, fractions, tax, payer, total, calculated shares)
- [ ] T101 [US4] Implement navigation: select bill → show detail → back to list
- [ ] T102 [US4] Add "View History" option to HomeScreen with keyboard shortcut (Ctrl+H)
- [ ] T103 [US4] Handle edge case: display "No bills entered yet" when history is empty

#### Integration & Testing

- [ ] T104 [US4] Write unit tests for bill retrieval methods (pagination, detail formatting)
- [ ] T105 [US4] Write integration test for history workflow in tests/integration/test_bill_history.py (create multiple bills, retrieve in order, verify detail accuracy)
- [ ] T106 [US4] Write TUI tests for HistoryScreen using pilot mode (list navigation, detail view, back navigation)

**Acceptance Criteria**:
1. ✅ User can navigate to history screen
2. ✅ User sees chronological list of all bills (most recent first)
3. ✅ User can select a bill to view full details
4. ✅ Bill details show all information: items, costs, assignments, fractions, tax, payer, total
5. ✅ User can verify calculations are correct
6. ✅ User can navigate back to list from detail view
7. ✅ Empty history shows helpful message
8. ✅ Pagination works correctly for large bill lists (>100 bills)
9. ✅ Test coverage ≥ 80% for history viewing code

---

## Phase 7: User Story 5 - TUI Usability and Responsiveness (Priority: P5)

**Goal**: Polish TUI with keyboard shortcuts, help system, and responsive layout.

**User Story**: As a user, I need a responsive TUI with keyboard shortcuts and help documentation so that I can work efficiently across different terminal environments.

**Independent Test**: Resize terminal to different dimensions, use keyboard shortcuts for navigation, access help, verify functionality and readability.

**Dependencies**: Requires Phases 3-6 completion (all screens exist).

### Tasks

#### Help System

- [ ] T107 [US5] Implement HelpScreen in splitfool/ui/screens/help.py (comprehensive help content with sections for each feature)
- [ ] T108 [US5] Document all keyboard shortcuts in help screen (Ctrl+N, Ctrl+B, Ctrl+V, Ctrl+H, F1/?, Esc, Enter, Tab, Arrow keys)
- [ ] T109 [US5] Document all features with usage instructions (user management, bill entry, balances, history)
- [ ] T110 [US5] Implement context-sensitive help (F1 shows help relevant to current screen)
- [ ] T111 [US5] Add "Help" option to HomeScreen with keyboard shortcut (F1 or ?)

#### Keyboard Shortcuts & Navigation

- [ ] T112 [US5] Implement global keyboard shortcuts across all screens (F1 for help, Esc to go back, Tab for navigation)
- [ ] T113 [US5] Implement screen-specific keyboard shortcuts (as defined in each screen's BINDINGS)
- [ ] T114 [US5] Ensure all actions have keyboard alternatives (no mouse required)
- [ ] T115 [US5] Implement focus management for form fields (Tab/Shift+Tab to navigate)

#### Responsive Layout

- [ ] T116 [US5] Implement responsive layout adapters for different terminal sizes (40x10, 80x24, 200x50)
- [ ] T117 [US5] Test layout in small terminal (40x10) - ensure critical elements visible with scrolling
- [ ] T118 [US5] Test layout in standard terminal (80x24) - ensure optimal layout
- [ ] T119 [US5] Test layout in large terminal (200x50) - ensure layout uses space effectively
- [ ] T120 [US5] Implement terminal resize handlers (gracefully handle resize events)

#### Visual Polish

- [ ] T121 [US5] Implement consistent color scheme across all screens (use Textual CSS)
- [ ] T122 [US5] Implement status indicators (success/error messages, loading states)
- [ ] T123 [US5] Implement proper focus indicators (highlight active input fields)
- [ ] T124 [US5] Add header/footer with app version and current screen name

#### Testing & Validation

- [ ] T125 [US5] Write TUI tests for keyboard navigation (all shortcuts work as documented)
- [ ] T126 [US5] Write TUI tests for terminal resize handling (app remains functional at all sizes)
- [ ] T127 [US5] Write TUI tests for help system (help accessible from all screens, content accurate)
- [ ] T128 [US5] Perform manual testing across different terminal emulators (verify ANSI support)

**Acceptance Criteria**:
1. ✅ User can access help from any screen (F1 or ?)
2. ✅ Help documentation is comprehensive and accurate
3. ✅ All features accessible via keyboard shortcuts
4. ✅ App is fully navigable without mouse
5. ✅ App works correctly in 40x10 terminal (with scrolling)
6. ✅ App works correctly in 80x24 terminal (optimal layout)
7. ✅ App works correctly in 200x50 terminal (uses space well)
8. ✅ App handles terminal resize gracefully (no crashes, layout updates)
9. ✅ Visual design is consistent and professional
10. ✅ 95%+ of user actions completable via keyboard (SC-006)

---

## Phase 8: Final Polish & Cross-Cutting Concerns

**Goal**: Address cross-cutting concerns, performance optimization, and final quality assurance.

**Deliverable**: Production-ready application meeting all success criteria.

### Tasks

#### Documentation

- [ ] T129 Update README.md with complete usage instructions, setup guide, and examples
- [ ] T130 Add inline code comments for complex algorithms (balance netting, tax distribution)
- [ ] T131 Generate API documentation from docstrings (optional, using Sphinx or pdoc)

#### Performance Optimization

- [ ] T132 Profile application startup time (target: <2 seconds per SC-004)
- [ ] T133 Profile UI responsiveness (target: <100ms render per SC-005)
- [ ] T134 Profile balance calculation performance (target: <5 seconds per SC-003)
- [ ] T135 Optimize database queries (add missing indexes if needed, verify query plans)
- [ ] T136 Test with large datasets (100 users, 1000 bills, 10k items per SC-008)

#### Error Recovery & Edge Cases

- [ ] T137 Implement database corruption recovery (detect corrupted DB, offer to reinitialize per FR-037)
- [ ] T138 Implement graceful error handling for all database errors (display user-friendly messages)
- [ ] T139 Test and handle all documented edge cases from spec.md
- [ ] T140 Implement input sanitization for all user inputs (prevent SQL injection via parameterized queries)

#### Final Testing & QA

- [ ] T141 Run full test suite and verify 80%+ overall coverage, 95%+ for business logic
- [ ] T142 Run mypy type checking with --strict mode (zero type errors)
- [ ] T143 Run ruff linting (zero linting errors)
- [ ] T144 Perform end-to-end manual testing of all user stories
- [ ] T145 Test data persistence (create data, close app, reopen, verify data intact)
- [ ] T146 Test error messages (verify all error codes present, messages clear and actionable)

#### Deployment Preparation

- [ ] T147 Create distribution package configuration in pyproject.toml
- [ ] T148 Test installation via `uv pip install` or similar
- [ ] T149 Create release notes documenting features and known issues
- [ ] T150 Tag release version in git (v1.0.0)

**Acceptance Criteria**:
1. ✅ All success criteria (SC-001 through SC-012) validated
2. ✅ Test coverage ≥ 80% overall, ≥ 95% for business logic
3. ✅ Zero type checking errors
4. ✅ Zero linting errors
5. ✅ All edge cases handled gracefully
6. ✅ Application performs within specified constraints
7. ✅ Documentation complete and accurate
8. ✅ Application ready for production use

---

## Task Dependencies & Execution Order

### Critical Path
```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational)
    ↓
Phase 3 (US1: User Management) ← MVP completion point
    ↓
Phase 4 (US2: Bill Entry) ← Requires users to exist
    ↓
Phase 5 (US3: Balance Viewing) ← Requires bills to exist
    ↓
Phase 6 (US4: Bill History) ← Requires bills to exist (can run parallel with Phase 5)
    ↓
Phase 7 (US5: TUI Polish) ← Requires all screens to exist
    ↓
Phase 8 (Final Polish)
```

### Parallelization Opportunities

**Within Phase 1 (Setup)**: Tasks T002-T008 can run in parallel after T001 completes.

**Within Phase 2 (Foundational)**:
- Utilities group (T013-T016) can run fully parallel
- Models group (T017-T023) can run fully parallel after utilities complete
- Repositories group (T027-T031) can run parallel after models complete
- Unit tests group (T033-T038) can run parallel after implementation complete

**Within Phase 3 (US1)**:
- After T039 (UserService) completes, all TUI components (T041-T047) can be built in parallel
- All test tasks (T048-T050) can run in parallel after implementation complete

**Within Phase 4 (US2)**:
- Repositories (T053-T054) can run parallel
- Service methods (T055-T060) have dependencies but some can overlap
- TUI widgets (T062-T067) can be built in parallel after T061 (BillEntryScreen) skeleton exists
- All test tasks (T072-T076) can run in parallel after implementation complete

**Within Phase 5 (US3)**:
- Service methods (T077-T083) have some dependencies but can overlap
- TUI components (T084-T089) can be built in parallel after T084 (BalanceViewScreen) skeleton exists
- All test tasks (T090-T094) can run in parallel after implementation complete

**Within Phase 6 (US4)**:
- TUI components (T098-T103) can be built in parallel after skeleton screen exists
- Test tasks (T104-T106) can run in parallel after implementation complete

**Within Phase 7 (US5)**:
- All groups can work in parallel: help system, keyboard shortcuts, responsive layout, visual polish
- Tests (T125-T128) can run in parallel after implementation complete

**Within Phase 8 (Final)**:
- Documentation (T129-T131), performance (T132-T136), and error recovery (T137-T140) can run in parallel
- Final QA (T141-T146) runs sequentially after all implementation complete

### Independent Story Implementation

After MVP (Phase 3), the following phases can be implemented independently by different developers:

- **Developer A**: Phase 4 (US2: Bill Entry) - most complex, requires deep understanding
- **Developer B**: Phase 5 (US3: Balance Viewing) - requires Phase 4 data but service layer can be built independently
- **Developer C**: Phase 6 (US4: Bill History) - can start immediately after Phase 4, completely independent of Phase 5
- **Developer D**: Phase 7 (US5: TUI Polish) - waits for all screens to exist, then polishes everything

This allows parallel workstreams after MVP delivery.

---

## Task Summary

| Phase | Task Range | Count | Estimated Time | Key Deliverable |
|-------|-----------|-------|----------------|-----------------|
| Phase 1: Setup | T001-T012 | 12 | 0.5 days | Working project skeleton |
| Phase 2: Foundational | T013-T038 | 26 | 2-3 days | Database layer, models, utilities |
| Phase 3: US1 (User Mgmt) | T039-T052 | 14 | 2-3 days | **MVP: Working user management** |
| Phase 4: US2 (Bill Entry) | T053-T076 | 24 | 5-7 days | Bill splitting with calculations |
| Phase 5: US3 (Balances) | T077-T095 | 19 | 3-4 days | Balance viewing and settlement |
| Phase 6: US4 (History) | T096-T106 | 11 | 2-3 days | Bill history viewing |
| Phase 7: US5 (Polish) | T107-T128 | 22 | 2-3 days | TUI polish and responsiveness |
| Phase 8: Final Polish | T129-T150 | 22 | 2-3 days | Production readiness |
| **Total** | **T001-T150** | **150** | **18-26 days** | **Complete feature** |

**Parallelization Benefit**: With 2-3 developers working in parallel after MVP, total calendar time can be reduced to ~12-15 days.

**MVP Time-to-Value**: 3-5 days (Phases 1-3)

---

## Getting Started

1. **Start with Phase 1**: Initialize project structure and dependencies
2. **Build Foundation (Phase 2)**: Implement all models, database layer, and utilities
3. **Deliver MVP (Phase 3)**: Complete user management for first working increment
4. **Iterate on User Stories**: Build out bill entry, balances, history, and polish
5. **Verify Quality**: Run full test suite, type checking, linting throughout
6. **Refer to Documentation**:
   - `plan.md` for architecture and technical decisions
   - `data-model.md` for entity definitions and database schema
   - `contracts/` for service interface contracts
   - `quickstart.md` for development workflow and commands
   - `.specify/memory/constitution.md` for code quality standards

**Remember**: Each phase should be independently testable. After Phase 3, you have a working application that can be demonstrated and used!

---

**Generated**: 2025-11-15  
**Status**: Ready for implementation  
**Next**: Begin with T001 (Initialize uv project)
