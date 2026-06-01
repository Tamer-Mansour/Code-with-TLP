# Classes, Interfaces, Records

## A class

```java
public class User {
    private final long id;
    private String name;

    public User(long id, String name) {
        this.id = id;
        this.name = name;
    }

    public long getId() { return id; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    @Override
    public String toString() {
        return "User[" + id + ", " + name + "]";
    }
}
```

The constructor name must match the class. `this` refers to the instance.

## Records (Java 14+)

For "data carrier" classes — immutable, with auto-generated `equals`, `hashCode`, `toString`, accessors:

```java
public record User(long id, String name, String email) {}
```

That's the whole class. Use it like:

```java
var u = new User(1, "Alice", "alice@x.com");
u.name();              // accessor (no get prefix)
new User(1, "Alice", "alice@x.com").equals(u);   // true
```

Records can't extend other classes (but can implement interfaces), and their components are `final`. Perfect for DTOs, value objects, and event payloads.

## Interfaces

```java
public interface Shape {
    double area();

    // default method - has a body, optional override
    default String describe() {
        return "Shape with area " + area();
    }

    // static utility
    static Shape square(double side) {
        return () -> side * side;       // implements area()
    }
}
```

A class can implement many interfaces:

```java
public class Circle implements Shape, Comparable<Circle> {
    private final double r;
    public Circle(double r) { this.r = r; }
    @Override public double area() { return Math.PI * r * r; }
    @Override public int compareTo(Circle o) { return Double.compare(r, o.r); }
}
```

## Sealed types (Java 17+)

Restrict who can extend or implement:

```java
public sealed interface Shape permits Circle, Square, Triangle {}

public final class Circle   implements Shape { ... }
public final class Square   implements Shape { ... }
public final class Triangle implements Shape { ... }
```

Now the compiler knows all the variants — combined with pattern matching, you get exhaustiveness:

```java
double area(Shape s) {
    return switch (s) {
        case Circle c   -> Math.PI * c.radius() * c.radius();
        case Square sq  -> sq.side() * sq.side();
        case Triangle t -> 0.5 * t.base() * t.height();
    };
}
```

Add a new shape → compiler errors at every switch.

## Abstract classes

```java
public abstract class Animal {
    public abstract String sound();
    public final String describe() { return "An animal that says " + sound(); }
}
```

Choose `abstract class` when you want shared fields + state; choose `interface` when you only need to share behavior.

## Visibility

| Modifier        | Visible to                            |
|-----------------|---------------------------------------|
| `public`        | everyone                              |
| `protected`     | same package + subclasses             |
| (default)       | same package                          |
| `private`       | declaring class only                  |

Default to `private` for fields; expose just enough through methods (or use records, which expose components by design).
