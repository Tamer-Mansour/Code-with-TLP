# Inheritance and Polymorphism

A class can `extends` exactly one other class. It inherits fields and non-private methods and can override them.

## Basic inheritance

```java
public class Animal {
    public String sound() { return "..."; }
}

public class Dog extends Animal {
    @Override
    public String sound() { return "woof"; }
}
```

`@Override` is optional but strongly recommended — the compiler verifies you actually override something. Catches a thousand subtle bugs.

## super

Call the parent's constructor or method:

```java
public class Puppy extends Dog {
    private final String owner;
    public Puppy(String owner) {
        super();
        this.owner = owner;
    }
    @Override
    public String sound() { return super.sound() + " (small)"; }
}
```

## Polymorphism

A reference of the parent type can hold a child instance:

```java
Animal a = new Dog();
a.sound();         // "woof" — dispatch by runtime type
```

This is **dynamic dispatch** — the JVM picks the right method based on the *actual* object, not the declared variable type.

## Casts and `instanceof`

```java
if (a instanceof Dog d) {
    d.sound();
}
```

Pattern variable (`d`) introduced in Java 16+ — narrower and cleaner than the old cast-after-check idiom.

## final classes and methods

`final` on a class means "can't be extended." On a method, "can't be overridden." Use for true value types (`String`, `Integer`, `LocalDate`).

```java
public final class ImmutablePoint { ... }
```

## Abstract methods

Declared without a body, in an abstract class:

```java
public abstract class Shape {
    public abstract double area();
    public String describe() { return "area=" + area(); }
}
```

Subclasses must implement `area()` or be abstract themselves.

## Composition over inheritance

A common pitfall: extending a class to reuse code, then fighting the parent's invariants forever. Prefer **composition** — hold a reference to a helper:

```java
// Inheritance — coupling forever
public class UserCache extends HashMap<Long, User> { ... }

// Composition — flexible, clear interface
public class UserCache {
    private final Map<Long, User> store = new ConcurrentHashMap<>();
    public User get(long id) { ... }
}
```

Inheritance is for "is-a" with a real subtype relationship (Dog **is an** Animal). Composition is for "has-a" reuse (UserCache **has a** Map).

## Method overloading vs overriding

- **Overloading** — same name, different parameter types. Resolved at compile time.
- **Overriding** — same name and signature in a subclass. Resolved at runtime.

```java
public void log(String s)        { ... }
public void log(int n)           { ... }   // overload — separate methods

@Override
public String toString()         { ... }    // override
```

## The "diamond problem" — interfaces

A class can't extend multiple classes, but can implement multiple interfaces — including ones with `default` methods. If two interfaces provide the same default, the class must explicitly choose one:

```java
class C implements A, B {
    @Override public void greet() { A.super.greet(); }
}
```
