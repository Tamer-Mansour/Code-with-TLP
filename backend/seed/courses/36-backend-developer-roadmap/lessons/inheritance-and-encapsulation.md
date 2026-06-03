# Inheritance and Encapsulation

Two pillars of object-oriented design — **encapsulation** and **inheritance** — give Java classes the ability to hide complexity and share behavior in a disciplined, maintainable way.

## Encapsulation

Encapsulation means bundling state (fields) and the logic that operates on it (methods) inside a class, and then controlling what the outside world can see. The tool is **access modifiers**.

| Modifier | Same class | Same package | Subclass | Everywhere |
|----------|:----------:|:------------:|:--------:|:----------:|
| `private` | yes | no | no | no |
| (package-private) | yes | yes | no | no |
| `protected` | yes | yes | yes | no |
| `public` | yes | yes | yes | yes |

The standard recipe: make fields `private`, expose them only through `public` getters and, where mutation is valid, setters.

```java
public class BankAccount {

    private final String id;   // immutable — no setter
    private double balance;    // mutable — guarded by methods

    public BankAccount(String id, double initialBalance) {
        if (initialBalance < 0) throw new IllegalArgumentException("Balance cannot be negative");
        this.id      = id;
        this.balance = initialBalance;
    }

    public String getId() { return id; }

    public double getBalance() { return balance; }

    public void deposit(double amount) {
        if (amount <= 0) throw new IllegalArgumentException("Deposit must be positive");
        balance += amount;
    }

    public boolean withdraw(double amount) {
        if (amount <= 0) throw new IllegalArgumentException("Amount must be positive");
        if (amount > balance) return false;
        balance -= amount;
        return true;
    }
}
```

Nothing outside the class can set `balance` directly. Every mutation goes through a method that enforces the invariant (balance never negative). This is the essence of encapsulation.

## Inheritance

Inheritance lets one class acquire the state and behavior of another. The subclass `extends` the superclass and may add new fields, override existing methods, or both.

```java
// Superclass
public class Animal {

    private final String name;

    public Animal(String name) {
        this.name = name;
    }

    public String getName() { return name; }

    public String speak() {
        return name + " makes a sound";
    }

    @Override
    public String toString() {
        return getClass().getSimpleName() + "[" + name + "]";
    }
}

// Subclass
public class Dog extends Animal {

    private final String breed;

    public Dog(String name, String breed) {
        super(name);          // must call superclass constructor first
        this.breed = breed;
    }

    public String getBreed() { return breed; }

    @Override
    public String speak() {
        return getName() + " barks";
    }
}

// Another subclass
public class Cat extends Animal {

    public Cat(String name) { super(name); }

    @Override
    public String speak() {
        return getName() + " meows";
    }
}
```

Using these classes:

```java
Animal[] animals = {
    new Dog("Rex", "Labrador"),
    new Cat("Whiskers"),
    new Dog("Buddy", "Poodle")
};

for (Animal a : animals) {
    System.out.println(a.speak());
}
// Rex barks
// Whiskers meows
// Buddy barks
```

This is **polymorphism at work**: the same `speak()` call produces different output depending on the runtime type. Java resolves the correct method at runtime (dynamic dispatch).

## `super` and Constructor Chaining

When a subclass is instantiated, the superclass constructor must run first. Use `super(...)` as the **first statement** of the subclass constructor. Forgetting it causes a compile error if the superclass has no no-arg constructor.

```java
public class SavingsAccount extends BankAccount {

    private double interestRate;

    public SavingsAccount(String id, double initialBalance, double interestRate) {
        super(id, initialBalance);          // delegate to BankAccount(String, double)
        if (interestRate < 0) throw new IllegalArgumentException("Rate cannot be negative");
        this.interestRate = interestRate;
    }

    public void applyInterest() {
        deposit(getBalance() * interestRate);
    }
}
```

`SavingsAccount` reuses the validation logic from `BankAccount.deposit()` rather than duplicating it.

## Method Overriding Rules

- Annotate with `@Override` — the compiler catches typos or mismatched signatures.
- The overriding method must have the **same signature** (name + parameter types).
- The return type may be a **covariant** (more specific) subtype.
- Cannot reduce visibility: a `public` method cannot be overridden as `protected`.
- `final` methods cannot be overridden; `final` classes cannot be subclassed.

## Common Mistakes

- **Exposing mutable fields as `public`** — bypasses all your validation logic.
- **Deep inheritance hierarchies (> 2–3 levels)** — prefer composition over deep inheritance.
- **Calling overridable methods in a constructor** — if a subclass overrides the method, it runs before the subclass's constructor body, leaving fields uninitialized.
- **Forgetting `@Override`** — an accidental overload (wrong parameter type) silently shadows the superclass method.

```java
// BUG: overload, not override — getName() in Animal still runs unchanged
public String getName(String prefix) {   // different signature!
    return prefix + super.getName();
}
```

Always write `@Override`; the compiler will tell you immediately if the signature is wrong.

## Encapsulation + Inheritance Together

Subclasses inherit `private` fields from the parent but **cannot access them directly** — they must use the parent's `public`/`protected` methods. This is intentional: the parent class can change its internal representation without breaking subclasses, as long as the public API stays the same.

If a subclass needs direct field access, mark the field `protected`. Reserve `protected` for fields that are genuinely part of the subclass contract; keep everything else `private`.

---

Encapsulation hides internal state behind a controlled interface; inheritance allows subclasses to specialize and extend that interface without duplicating code. Together, they are the foundation for building modular, maintainable Java applications.
