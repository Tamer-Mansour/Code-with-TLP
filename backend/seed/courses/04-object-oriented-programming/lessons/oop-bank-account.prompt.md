# Bank Account Command Processor

Implement a `BankAccount` class that processes a sequence of commands read from standard input.

## Commands

Each line of input contains one command:

- `DEPOSIT <amount>` — add `amount` to the balance (amount is a positive integer)
- `WITHDRAW <amount>` — subtract `amount` from the balance; if insufficient funds, print `INSUFFICIENT FUNDS` and leave the balance unchanged
- `BALANCE` — print the current balance as an integer

## Input Format

The first line is an integer `N` — the number of commands that follow.
The next `N` lines each contain one command.

The account starts with a balance of `0`.

## Output Format

For each `BALANCE` command, print the current balance on its own line.
For each failed `WITHDRAW`, print `INSUFFICIENT FUNDS` on its own line.
Successful `DEPOSIT` and `WITHDRAW` commands produce no output.

## Example

**Input:**
```
5
DEPOSIT 100
WITHDRAW 30
BALANCE
WITHDRAW 200
BALANCE
```

**Output:**
```
70
INSUFFICIENT FUNDS
70
```
