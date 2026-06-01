# Classes, Records, Structs

C# has three ways to define a custom type. Knowing when to use each is the most consequential modeling decision in idiomatic C#.

## Class — reference type with behavior

```csharp
public class User
{
    public long Id { get; }
    public string Name { get; set; }
    public string Email { get; init; }       // settable only in initializer

    public User(long id, string name, string email)
    {
        Id = id;
        Name = name;
        Email = email;
    }

    public string Greet() => $"Hi, {Name}";
}
```

- **Reference type** — passed by reference, compared by reference (`==` checks identity).
- Use for entities with state and behavior.
- Use when you need inheritance (a class can extend one base class).

`init` is like `set` but only in object initializers — immutable after construction.

## Record — value-equal, mostly immutable

```csharp
public record User(long Id, string Name, string Email);

var a = new User(1, "Alice", "a@x.com");
var b = new User(1, "Alice", "a@x.com");
a == b;                           // true — value equality
var c = a with { Name = "Alicia" };  // non-destructive copy
```

`record` auto-generates:

- Constructor (positional).
- `Equals`, `GetHashCode`, `ToString` based on values.
- The `with` expression for clean immutable updates.

Records are **reference types** (under the hood). For value-type equality semantics on small data structures, `record struct`:

```csharp
public record struct Point(double X, double Y);
```

## Struct — value type

```csharp
public struct Point
{
    public double X { get; }
    public double Y { get; }
    public Point(double x, double y) { X = x; Y = y; }
}
```

- **Copied on assignment and parameter passing.**
- No GC allocation in many contexts (stack or inline).
- Compared by value (with `IEquatable` implementation; or `record struct` does it for you).

Use for **small, immutable data** (≤ 16 bytes-ish): coordinates, IDs wrapped in strong types, color values. Big structs hurt — they get copied around.

## Interface

```csharp
public interface IGreeter
{
    string Greet();

    // default implementation (C# 8+)
    string Wave() => "👋";
}

public class FormalGreeter : IGreeter
{
    public string Greet() => "Good day.";
}
```

A class can implement many interfaces. Default method bodies make it easy to extend an interface without breaking existing implementers.

## Inheritance

```csharp
public class Animal
{
    public virtual string Sound() => "...";
}

public class Dog : Animal
{
    public override string Sound() => "woof";
}
```

`virtual` allows override; `override` confirms it; `sealed` prevents further override.

A class can inherit from one base + implement many interfaces.

## Properties

```csharp
public class Account
{
    public decimal Balance { get; private set; }   // get public, set private

    private decimal _balance;
    public decimal Balance2
    {
        get => _balance;
        set => _balance = value >= 0 ? value : throw new ArgumentException();
    }
}
```

`{ get; set; }` is shorthand for the field + getter/setter pair. Prefer this over public fields.

## When to choose

| Need                                     | Choose       |
|------------------------------------------|--------------|
| Entity with identity                     | class        |
| Data carrier, value-equal                | record       |
| Tiny immutable value (Point, Money)      | record struct|
| Performance-critical hot loop, small data| struct       |
| Multiple-implementation contract         | interface    |
| Common code + extension                  | abstract class |

Default to **record** for new data shapes. Reach for **class** when you have stateful behavior. Reach for **struct** when measured profiling demands.
