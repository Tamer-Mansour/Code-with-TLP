# Types and Operators

Java is **statically typed**: every variable's type is known at compile time. Types split into **primitives** and **objects**.

## Primitives

| Type      | Size  | Range                  |
|-----------|-------|------------------------|
| `byte`    | 1B    | -128 to 127            |
| `short`   | 2B    | ±32767                 |
| `int`     | 4B    | ±2.1 billion           |
| `long`    | 8B    | ±9.2e18                |
| `float`   | 4B    | IEEE-754               |
| `double`  | 8B    | IEEE-754               |
| `char`    | 2B    | UTF-16 code unit       |
| `boolean` | 1B    | true / false           |

Literals:

```java
int n = 1_000_000;          // _ allowed for readability
long big = 9_223_372_036_854_775_807L;     // L suffix
float f = 3.14F;
double d = 3.14;
char c = 'A';
boolean ok = true;
```

## Strings — objects, not primitives

```java
String s = "hello";
String t = "world";
String greeting = s + ", " + t;
String formatted = "Hello, %s. You are %d.".formatted("Alice", 30);
```

Text blocks (Java 13+):

```java
String json = """
        {
          "name": "Alice",
          "age": 30
        }
        """;
```

## var — local-variable inference

```java
var name = "Alice";          // String
var users = new ArrayList<User>();
```

`var` only works for locals — not parameters, fields, or returns. Use it to remove repetition; don't use it where the type makes the code clearer.

## Wrapper types

Every primitive has a corresponding object wrapper:

```
int → Integer
long → Long
boolean → Boolean
char → Character
double → Double
```

Auto-boxing and unboxing convert silently:

```java
List<Integer> xs = List.of(1, 2, 3);     // int auto-boxes to Integer
int first = xs.get(0);                    // Integer auto-unboxes to int
```

Watch out: `null` can hide in a `Long` and crash on unbox.

## Equality

```java
"hello" == "hello"           // unreliable (compares references)
"hello".equals("hello")      // true (compares value)
```

Always use `.equals()` for objects. `==` is reference identity (true by accident for interned strings).

## Operators

```java
+ - * / %        // arithmetic; / between ints is integer division
++ --            // pre/post increment
== != < > <= >=  // comparison
&& || !          // logical (short-circuit)
& | ^ ~          // bitwise (NOT short-circuit on booleans)
<< >> >>>        // shifts (>>> is unsigned)
```

`5 / 2 == 2` (int), `5.0 / 2 == 2.5` (double). Mind your types.

## final

A `final` variable can't be reassigned. Locals, fields, and parameters can all be final:

```java
final int LIMIT = 100;
public void f(final List<Integer> xs) { ... }
```

For fields, `final` enforces immutability. For locals, it's a hint that the value is fixed. Many codebases use `final` aggressively in method parameters; modern style leans toward implicit immutability via `record`s instead.

## null

A reference can be null. Dereferencing null throws `NullPointerException`. The modern remedy: `Optional<T>` for return types where absence is meaningful.

```java
Optional<User> findUser(long id) { ... }

findUser(42).ifPresent(u -> System.out.println(u.name()));
```
