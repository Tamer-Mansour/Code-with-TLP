# Exercise: Bank Account Simulation

Encapsulation is the OOP principle of bundling state with the methods that control it, and restricting direct access from outside. A bank account is the textbook example: the balance is private, and the only way to change it is through `deposit()` and `withdraw()` methods that enforce business rules.

## Java design

```java
public class BankAccount {
    private int balance;

    public BankAccount(int initialBalance) {
        this.balance = initialBalance;
    }

    public void deposit(int amount) {
        balance += amount;
        System.out.println(balance);
    }

    public boolean withdraw(int amount) {
        if (amount > balance) {
            System.out.println("Insufficient funds");
            return false;
        }
        balance -= amount;
        System.out.println(balance);
        return true;
    }

    public void printBalance() {
        System.out.println(balance);
    }
}
```

Key OOP ideas in this design:
- **Private field**: `balance` cannot be read or written directly from outside the class.
- **Constructor**: sets up initial state when the object is created.
- **Access modifiers**: `public` methods form the controlled interface to the private state.
- **Guard clause**: `withdraw` checks the invariant (`amount <= balance`) before mutating state.

## Problem statement

Simulate a bank account. Read the initial balance (integer) on the first line. Then read a series of commands until EOF:

- `deposit X` — add `X` to the balance; print the new balance.
- `withdraw X` — if `X > balance`, print `Insufficient funds` and leave the balance unchanged; otherwise subtract and print the new balance.
- `balance` — print the current balance without changing it.

### Example

Input:
```
100
deposit 50
balance
withdraw 200
withdraw 30
balance
```

Output:
```
150
150
Insufficient funds
120
120
```

## Important Java note

When you pass an object to a method, Java passes the **reference by value** — a copy of the reference. This means the method can call `account.deposit(50)` and mutate the account's fields through that copied reference. However, the method **cannot** reassign the caller's variable to point to a different object. Many beginner texts incorrectly say "objects are passed by reference" — the precise term is "pass-by-value of the reference."

## Further reading

- David J. Eck, *Introduction to Programming Using Java* (9th ed.) — Chapter 5: Objects and Classes: https://math.hws.edu/javanotes/
- MIT OCW 6.092 — Lecture 3 covers object-oriented programming: https://ocw.mit.edu/courses/6-092-introduction-to-programming-in-java-january-iap-2010/
