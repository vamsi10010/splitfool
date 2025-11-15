---
agent: speckit.specify
---

Develop splitfool. Splitfool is a TUI application for splitting bills
among multiple users. As a user, this is how I would use splitfool:
- I launch splitfool from the command line
- I see a rich TUI interface with multiple options
- I can add, modify, and delete users. 
- I can view outstanding balances for each user. Users owe money to each other.
- I can clear/settle balances between users.
- I can open the TUI later and see my previous data (everything is saved
in a local database).
- In the TUI, I can add a new bill. Bill entry is completely manual.
- When adding a bill, I can do the following:
    - Add an item with cost
    - Assign the item to one or more users
    - Assign different fractions of the item to each assigned user (default
    to equal split)
    - Add tax + other costs to the bill
    - Specify who paid the bill (one user)
    - See total cost of the bill
    - See how much each user owes for the bill
    - Be able to modify items, assigned users, fractions, tax, payer
      before finalizing the bill
- After adding the bill, the balances of all users are updated accordingly.
- I can view a history of all bills added, with details.
- The TUI is responsive and works well on different terminal sizes.
- The TUI has keyboard shortcuts for common actions.
- The TUI has a help section that explains how to use the application.
- The application is robust and handles invalid inputs gracefully.
