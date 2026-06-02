# What Is Encapsulation?

Encapsulation is the OOP principle of **bundling data and the functions that operate on it into a single unit** (the class), while controlling which parts of that bundle are visible to the outside world. It is not simply about adding `private:` — it is about defining **who owns the data and who is responsible for keeping it consistent**.

## The Core Idea

Without encapsulation you have a struct that anyone can reach into and corrupt:

```cpp
struct BankAccount {
    double balance;      // anyone can write a negative value
    int    transactions; // caller must remember to update this too
};

BankAccount acc;
acc.balance = -500.0;   // no guard, invariant broken
```

With encapsulation the class enforces its own rules:

```cpp
class BankAccount {
public:
    bool deposit(double amount) {
        if (amount <= 0) return false;
        balance_     += amount;
        transactions_++;
        return true;
    }
    double balance() const { return balance_; }

private:
    double balance_     = 0.0;
    int    transactions_= 0;
};
```

Now `balance_` can never go below zero via `deposit`, and the `transactions_` counter is always in sync — **the invariant is owned by the class**.

## Access Specifiers in C++

| Specifier   | Visible to                                      |
|-------------|-------------------------------------------------|
| `public`    | Everyone                                        |
| `protected` | The class and its subclasses                    |
| `private`   | Only the class itself (and `friend` declarations)|

`struct` members are `public` by default; `class` members are `private` by default. Choose `class` when you intend encapsulation; `struct` for plain data aggregates.

## What Encapsulation Buys You

- **Invariant enforcement** — the object is always in a valid state if every mutating operation goes through the public interface.
- **Freedom to refactor internals** — callers do not depend on storage layout, so you can swap a `double` for a `long long` cents representation without touching call sites.
- **Reduced coupling** — downstream code depends on the *interface*, not on how the sausage is made.
- **Easier testing** — you test the contract (public methods), not arbitrary memory.

## Common Pitfalls

- **Returning a non-const reference to a private member** defeats encapsulation entirely.
- **Over-exposing via `friend`** — use sparingly; every `friend` is a hole in the wall.
- **Trivial getters + setters for every field** — if external code needs to set every field individually the class is not really encapsulating anything; reconsider the design.

## Worked Example: Temperature Sensor

```cpp
class TemperatureSensor {
public:
    // Returns false if raw ADC value is out of valid hardware range
    bool set_raw(int adc) {
        if (adc < 0 || adc > 4095) return false; // 12-bit ADC
        raw_ = adc;
        return true;
    }

    // Converts once, on demand
    float celsius() const {
        // Datasheet formula: Tc = (raw / 4095.0) * 330.0 - 40.0
        return (raw_ / 4095.0f) * 330.0f - 40.0f;
    }

private:
    int raw_ = 0;
};
```

Callers never see `raw_`; the conversion formula lives in one place; changing the formula or the ADC resolution is a one-line edit.

## Interview Answer

> "Encapsulation bundles data with the operations that manage it and restricts direct access so the class can enforce its own invariants, letting you change the internal representation without breaking callers."
