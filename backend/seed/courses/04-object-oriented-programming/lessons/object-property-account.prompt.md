# Property-Validated Account

## Problem Statement

Build a `BankAccount` class that uses a `@property` to expose `balance` as read-only and encapsulates all mutations behind methods that print formatted messages.

**Class requirements:**

- `__init__(self, owner)` — stores `owner` and sets `self._balance = 0`.
- `balance` — a `@property` that returns `self._balance` (read-only; no setter needed).
- `deposit(amount)` — adds `amount` to `_balance`. Prints: `"Deposited <amount>. Balance: <new_balance>"`.
- `withdraw(amount)` — subtracts `amount` if funds are sufficient. Prints: `"Withdrew <amount>. Balance: <new_balance>"`. If insufficient, prints: `"Insufficient funds. Balance: <current_balance>"` without changing `_balance`.
- `get_balance()` — prints: `"Balance: <current_balance>"`.

**Input format:**

- First line: integer `N` — number of commands.
- Next `N` lines: one of `DEPOSIT <amount>`, `WITHDRAW <amount>`, or `BALANCE`.
- `<amount>` is always a positive integer.

**Output format:**

Each command that produces output prints exactly one line as specified above. No output for unknown commands.

## Examples

**Example 1**

Input:
```
5
DEPOSIT 500
DEPOSIT 200
WITHDRAW 100
WITHDRAW 1000
BALANCE
```

Output:
```
Deposited 500. Balance: 500
Deposited 200. Balance: 700
Withdrew 100. Balance: 600
Insufficient funds. Balance: 600
Balance: 600
```

**Example 2**

Input:
```
1
BALANCE
```

Output:
```
Balance: 0
```

**Example 3**

Input:
```
3
DEPOSIT 50
WITHDRAW 50
BALANCE
```

Output:
```
Deposited 50. Balance: 50
Withdrew 50. Balance: 0
Balance: 0
```

**Example 4**

Input:
```
3
WITHDRAW 10
WITHDRAW 1
BALANCE
```

Output:
```
Insufficient funds. Balance: 0
Insufficient funds. Balance: 0
Balance: 0
```

**Example 5**

Input:
```
6
DEPOSIT 500
WITHDRAW 100
BALANCE
DEPOSIT 50
WITHDRAW 600
BALANCE
```

Output:
```
Deposited 500. Balance: 500
Withdrew 100. Balance: 400
Balance: 400
Deposited 50. Balance: 450
Insufficient funds. Balance: 450
Balance: 450
```

## Constraints

- 1 ≤ N ≤ 100
- 1 ≤ amount ≤ 10,000
