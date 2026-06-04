# Bank Account Simulation

Simulate a bank account with encapsulation.

Read an initial balance (integer) on the first line. Then read commands one per line until EOF. Each command is one of:

- `deposit X` — add `X` to the balance; print the resulting balance.
- `withdraw X` — if `X > balance`, print `Insufficient funds` and leave the balance unchanged; otherwise subtract `X` and print the resulting balance.
- `balance` — print the current balance (no change).

## Input format

```
<initial_balance>
<command> [amount]
...
```

## Output format

One line per command, as described above.

## Example

**Input**
```
100
deposit 50
balance
withdraw 200
withdraw 30
balance
```

**Output**
```
150
150
Insufficient funds
120
120
```

## Constraints

- `0 <= initial_balance <= 10^6`
- `1 <= X <= 10^6` for deposit/withdraw
- At most 1000 commands
