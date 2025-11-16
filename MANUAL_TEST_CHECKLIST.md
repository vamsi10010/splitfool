# Manual End-to-End Test Checklist

Use this checklist to verify all functionality before release.

## Pre-Test Setup
- [ ] Clean database: `rm splitfool.db` (or use fresh path)
- [ ] Launch app: `uv run splitfool`
- [ ] Terminal size: 80x24 or larger

## Test 1: User Management (US1)
- [ ] Add user "Alice" successfully
- [ ] Add user "Bob" successfully  
- [ ] Add user "Carol" successfully
- [ ] Try to add duplicate "Alice" → should fail with error
- [ ] Edit "Bob" to "Bobby" → should succeed
- [ ] Try to delete user → confirmation dialog appears
- [ ] Confirm deletion of a user with no balances → should succeed
- [ ] Verify users persist: quit app, relaunch, users still present

## Test 2: Bill Entry (US2)
- [ ] Navigate to "New Bill" (Ctrl+B)
- [ ] Enter description: "Dinner"
- [ ] Select payer: Alice
- [ ] Add item: "Pizza" $30.00
- [ ] Assign Pizza to Alice, Bobby, Carol equally (0.33, 0.33, 0.34)
- [ ] Add item: "Salad" $15.00
- [ ] Assign Salad to Bobby, Carol equally (0.5, 0.5)
- [ ] Add tax: $12.00
- [ ] Preview shows:
  - Alice owes: calculated amount
  - Bobby owes: calculated amount  
  - Carol owes: calculated amount
- [ ] Finalize bill → should save successfully
- [ ] Verify bill persists: check history

## Test 3: Balance Viewing (US3)
- [ ] Navigate to Balance View (Ctrl+V)
- [ ] Verify balances shown correctly:
  - Bobby owes Alice: $X.XX
  - Carol owes Alice: $Y.YY
- [ ] Amounts match preview from bill entry

## Test 4: Adding More Bills
- [ ] Create second bill with Bobby as payer
- [ ] Assign items differently
- [ ] Verify balance view updates with netted amounts
- [ ] Check for mutual debt netting (if applicable)

## Test 5: Settlement (US3)
- [ ] From Balance View, select "Settle All Balances"
- [ ] Confirmation dialog shows current balances
- [ ] Confirm settlement
- [ ] Verify all balances now show $0.00 or "All balances settled"
- [ ] Check history still shows previous bills
- [ ] Create new bill after settlement
- [ ] Verify new balance appears correctly

## Test 6: Bill History (US4)
- [ ] Navigate to History (Ctrl+H)
- [ ] Verify all bills listed chronologically (newest first)
- [ ] Select a bill to view details
- [ ] Verify details show:
  - Description, payer, timestamp
  - All items with costs
  - All assignments with fractions
  - Tax amount
  - Calculated shares
- [ ] Navigate back to list

## Test 7: User Deletion with Balances
- [ ] Create bill with balances outstanding
- [ ] Try to delete user with balance → should be blocked
- [ ] Error message explains user has outstanding balances
- [ ] Settle balances
- [ ] Try delete again → should succeed

## Test 8: Help System (US5)
- [ ] Press F1 or ?
- [ ] Verify help screen shows:
  - All keyboard shortcuts
  - Feature descriptions
  - Usage instructions
- [ ] Help accessible from all screens

## Test 9: Keyboard Navigation (US5)
- [ ] Navigate entire app using only keyboard
- [ ] Tab between fields
- [ ] Arrow keys in lists
- [ ] Enter to select
- [ ] Esc to go back
- [ ] Verify 95%+ actions work without mouse

## Test 10: Terminal Responsiveness (US5)
- [ ] Resize terminal to 40x10 → app still functional (may scroll)
- [ ] Resize to 80x24 → optimal layout
- [ ] Resize to 200x50 → uses space effectively
- [ ] No crashes on resize

## Test 11: Data Persistence
- [ ] Create several bills and users
- [ ] Note current balances
- [ ] Quit app (Ctrl+Q or close)
- [ ] Relaunch app
- [ ] Verify all data intact:
  - Users present
  - Bills in history
  - Balances calculated correctly

## Test 12: Error Handling
- [ ] Try empty user name → validation error
- [ ] Try name over 100 chars → validation error
- [ ] Try bill with no items → validation error
- [ ] Try item with $0 cost → validation error
- [ ] Try fractions not summing to 1.0 → validation error
- [ ] All errors show clear, actionable messages

## Test 13: Database Recovery
- [ ] Run: `uv run splitfool --check-db` → should pass
- [ ] Corrupt database manually (optional)
- [ ] Run: `uv run splitfool --recover-db` → should recreate
- [ ] Verify app launches with fresh database

## Test Results Summary

Date: ___________
Tester: ___________

Pass/Fail: ___________
Issues Found: ___________

Notes:
___________________________________________________________
___________________________________________________________
___________________________________________________________
