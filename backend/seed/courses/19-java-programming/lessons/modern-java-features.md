# Modern Java Features (Java 14–21)

Java has evolved rapidly since Java 8. These features make the language more expressive and safer.

## Pattern Matching for instanceof (Java 16)

Old way:

```java
if (obj instanceof String) {
    String s = (String) obj;   // redundant cast
    System.out.println(s.length());
}
```

New way:

```java
if (obj instanceof String s) {
    System.out.println(s.length()); // s is in scope and typed
}
```

## Sealed Classes (Java 17)

Restrict which classes can implement/extend an interface or class:

```java
public sealed interface Shape
    permits Circle, Rectangle, Triangle {}

public record Circle(double radius) implements Shape {}
public record Rectangle(double w, double h) implements Shape {}
public record Triangle(double base, double height) implements Shape {}
```

Combined with pattern matching, this enables exhaustive switches:

```java
double area = switch (shape) {
    case Circle c    -> Math.PI * c.radius() * c.radius();
    case Rectangle r -> r.w() * r.h();
    case Triangle t  -> 0.5 * t.base() * t.height();
};
// No default needed — compiler knows all cases are covered
```

## Switch Expressions (Java 14)

Switch can now be an expression that returns a value:

```java
String label = switch (day) {
    case MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY -> "Weekday";
    case SATURDAY, SUNDAY -> "Weekend";
};

// With a block (use yield to return)
int numLetters = switch (day) {
    case MONDAY, FRIDAY, SUNDAY -> 6;
    case TUESDAY -> 7;
    default -> {
        String s = day.toString();
        yield s.length();
    }
};
```

## Text Blocks (Java 15)

Multi-line string literals without escaping:

```java
String json = """
        {
            "name": "Alice",
            "age": 30
        }
        """;

String sql = """
        SELECT *
        FROM users
        WHERE active = true
        ORDER BY name;
        """;
```

Indentation is automatically stripped to the least-indented line.

## Records (Java 16)

Concise immutable data carriers:

```java
record Person(String name, int age) {
    // Compact canonical constructor — add validation
    Person {
        if (age < 0) throw new IllegalArgumentException("Age negative");
    }

    // Custom methods allowed
    String greeting() {
        return "Hi, I'm " + name;
    }
}

var alice = new Person("Alice", 30);
System.out.println(alice.name());     // "Alice"
System.out.println(alice);            // Person[name=Alice, age=30]
```

Auto-generated: canonical constructor, getters, `equals`, `hashCode`, `toString`.

## var — Local Variable Type Inference (Java 10)

```java
var list = new ArrayList<String>();  // inferred: ArrayList<String>
var map  = Map.of("a", 1, "b", 2);  // Map<String, Integer>
var line = reader.readLine();        // String

// Only for local variables — not fields, not method return types
for (var entry : map.entrySet()) {
    System.out.println(entry.getKey() + "=" + entry.getValue());
}
```

## String methods (Java 11–15)

```java
" hello ".strip();       // "hello" — Unicode-aware (prefer over trim())
"  ".isBlank();          // true
"a\nb\nc".lines()        // Stream<String>
"abc".repeat(3);         // "abcabcabc"
String.format("%-10s|", "hi"); // "hi        |"
// Java 15+
"  hello  ".stripLeading();  // "hello  "
"  hello  ".stripTrailing(); // "  hello"
```

## Feature availability summary

| Feature | Since |
|---------|-------|
| `var` | Java 10 |
| Switch expressions | Java 14 |
| Text blocks | Java 15 |
| Records | Java 16 |
| Pattern matching instanceof | Java 16 |
| Sealed classes | Java 17 |
| Virtual threads (Project Loom) | Java 21 |

## Virtual Threads (Java 21) — brief preview

Virtual threads are lightweight threads managed by the JVM, not the OS. They make blocking I/O code scale like non-blocking code without changing your programming model:

```java
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    for (int i = 0; i < 100_000; i++) {
        int id = i;
        executor.submit(() -> {
            Thread.sleep(100); // blocking, but cheap with virtual threads
            System.out.println("Task " + id + " done");
        });
    }
} // auto-shutdown
```

You can create a million virtual threads without exhausting OS thread limits.
