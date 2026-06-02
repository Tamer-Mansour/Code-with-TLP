# Inheritance and Polymorphism

C# supports single-class inheritance plus multiple interface implementation. Understanding virtual dispatch and how `override`, `sealed`, and `abstract` interact is essential for writing extensible, maintainable class hierarchies.

## Base and derived classes

```csharp
public class Shape
{
    public string Color { get; set; } = "white";

    public virtual double Area() => 0;

    public override string ToString() =>
        $"{GetType().Name} ({Color}), area={Area():F2}";
}

public class Circle : Shape
{
    public double Radius { get; init; }

    public override double Area() => Math.PI * Radius * Radius;
}

public class Rectangle : Shape
{
    public double Width  { get; init; }
    public double Height { get; init; }

    public override double Area() => Width * Height;
}
```

`virtual` marks a method as overridable. `override` in the subclass replaces the parent implementation.

## Polymorphism in action

```csharp
Shape[] shapes =
{
    new Circle    { Radius = 5, Color = "red" },
    new Rectangle { Width = 4, Height = 6, Color = "blue" },
};

foreach (var s in shapes)
    Console.WriteLine(s);        // calls the overridden Area() and ToString()
```

Output:
```
Circle (red), area=78.54
Rectangle (blue), area=24.00
```

## abstract classes

An `abstract` class cannot be instantiated — it exists only as a base. It may contain abstract methods (no body) that subclasses *must* implement:

```csharp
public abstract class Animal
{
    public string Name { get; }
    protected Animal(string name) => Name = name;

    public abstract string Sound();   // must be implemented

    public void Describe() =>
        Console.WriteLine($"{Name} says {Sound()}");
}

public class Dog : Animal
{
    public Dog(string name) : base(name) { }
    public override string Sound() => "Woof";
}
```

## sealed classes and methods

`sealed` prevents further inheritance or overriding:

```csharp
public sealed class Singleton { ... }  // cannot be subclassed

public class Base
{
    public virtual void Foo() { }
}
public class Mid : Base
{
    public sealed override void Foo() { } // no further overriding
}
```

Sealing a class also enables JIT devirtualization, a minor performance benefit.

## Calling base members

Use `base` to call the parent's version of a member:

```csharp
public class Square : Rectangle
{
    public Square(double side) : base()
    {
        Width  = side;
        Height = side;
    }

    public override string ToString() =>
        $"Square — {base.ToString()}";  // reuse parent's ToString
}
```

## Choosing: abstract class vs. interface

| Aspect                     | Abstract class            | Interface                        |
|----------------------------|---------------------------|----------------------------------|
| Multiple inheritance       | No                        | Yes (multiple interfaces)        |
| State (fields)             | Yes                       | No (only properties, no fields)  |
| Constructor                | Yes                       | No                               |
| Default implementation     | Yes (regular methods)     | C# 8+ default interface methods  |
| Best for                   | Shared base behavior      | Contracts / capabilities         |

Use an **abstract class** when you have shared state or behavior across a family. Use an **interface** when you want to express a capability that unrelated types can share.

## is and as for type testing

```csharp
Shape s = new Circle { Radius = 3 };

if (s is Circle c)
    Console.WriteLine($"Circle with radius {c.Radius}");

// as returns null instead of throwing
var r = s as Rectangle;
Console.WriteLine(r is null ? "not a rectangle" : "rectangle");
```

## Key takeaways

- Mark methods `virtual` to allow overriding; `override` to replace them in subclasses.
- `abstract` forces subclasses to provide an implementation.
- `sealed` locks down a class or method from further extension.
- Prefer interfaces for capabilities, abstract classes for shared state/behavior.
