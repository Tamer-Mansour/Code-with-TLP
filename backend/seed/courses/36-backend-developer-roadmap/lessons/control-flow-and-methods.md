# Control Flow and Methods

Java's control-flow constructs follow the C-family style, while its method system enforces strict typing and supports modern features like switch expressions and varargs. Mastering both is essential before moving on to object-oriented design and Spring components.

## Conditional Statements

The classic `if / else if / else` chain evaluates boolean expressions top-to-bottom and executes the first matching block.

```java
int httpStatus = 404;

if (httpStatus == 200) {
    System.out.println("OK");
} else if (httpStatus == 404) {
    System.out.println("Not Found");
} else {
    System.out.println("Other: " + httpStatus);
}
```

Java 14+ introduced **switch expressions**, which return a value and eliminate accidental fall-through:

```java
String label = switch (httpStatus) {
    case 200       -> "OK";
    case 400       -> "Bad Request";
    case 404       -> "Not Found";
    case 500       -> "Server Error";
    default        -> "Unknown (" + httpStatus + ")";
};
System.out.println(label); // Not Found
```

The arrow (`->`) form does not fall through and does not need `break`. Use the classic `case X:` form only when you intentionally need fall-through behavior.

## Loops

| Loop type    | When to use                                              |
|--------------|----------------------------------------------------------|
| `for`        | Known iteration count; index needed                      |
| `for-each`   | Iterating a collection or array; index not needed        |
| `while`      | Condition checked before each iteration                  |
| `do-while`   | Body must run at least once (e.g., menu prompts)         |

```java
// Classic for — iterating with an index
for (int i = 0; i < 5; i++) {
    System.out.println("step " + i);
}

// Enhanced for — cleaner when index is irrelevant
String[] roles = {"USER", "ADMIN", "MODERATOR"};
for (String role : roles) {
    System.out.println(role);
}

// while — poll until a condition changes
int retries = 0;
while (retries < 3) {
    System.out.println("Attempt " + (retries + 1));
    retries++;
}

// do-while — body executes before the first check
int input;
do {
    input = readIntFromConsole(); // hypothetical helper
} while (input < 1 || input > 10);
```

`break` exits the innermost loop immediately; `continue` skips to the next iteration. A **labeled break** exits an outer loop from inside a nested one:

```java
outer:
for (int row = 0; row < 3; row++) {
    for (int col = 0; col < 3; col++) {
        if (row == 1 && col == 1) break outer; // exits both loops
        System.out.println(row + "," + col);
    }
}
```

## Defining and Calling Methods

A method in Java has: access modifier, optional `static`, return type, name, parameter list, and body.

```java
public class MathUtils {

    // Static utility — no instance needed
    public static int add(int a, int b) {
        return a + b;
    }

    // Returns nothing
    public static void printDivider(int width) {
        System.out.println("-".repeat(width));
    }

    // Overloaded — same name, different parameter types
    public static double add(double a, double b) {
        return a + b;
    }
}
```

Call a static method by class name:

```java
int result = MathUtils.add(3, 7);       // 10
double r2   = MathUtils.add(1.5, 2.5); // 4.0  (overloaded version)
MathUtils.printDivider(20);
```

## Varargs

When the number of arguments is unknown at compile time, use varargs (`Type... name`). It must be the last parameter.

```java
public static int sum(int... numbers) {
    int total = 0;
    for (int n : numbers) {
        total += n;
    }
    return total;
}

System.out.println(sum(1, 2, 3));       // 6
System.out.println(sum(10, 20, 30, 40)); // 100
```

## Worked Example: HTTP Status Classifier

The following method combines a switch expression with a loop to classify a list of status codes — a pattern you will see repeatedly in Spring controller tests and integration suites.

```java
import java.util.List;

public class StatusClassifier {

    public static String classify(int code) {
        return switch (code / 100) {
            case 2  -> "Success";
            case 3  -> "Redirect";
            case 4  -> "Client Error";
            case 5  -> "Server Error";
            default -> "Informational or Unknown";
        };
    }

    public static void main(String[] args) {
        List<Integer> codes = List.of(200, 301, 400, 404, 500, 503);

        for (int code : codes) {
            System.out.printf("%d -> %s%n", code, classify(code));
        }
    }
}
```

Output:

```
200 -> Success
301 -> Redirect
400 -> Client Error
404 -> Client Error
500 -> Server Error
503 -> Server Error
```

## Common Mistakes and Best Practices

- **Missing `break` in classic switch** — without `break`, execution falls through to the next case. Prefer arrow-style switch expressions to avoid this entirely.
- **Infinite loops** — always ensure the loop variable is updated, or that the terminating condition can eventually become `false`.
- **Method length** — keep methods focused on a single responsibility. If a method exceeds ~20 lines, consider extracting helper methods.
- **Overloading vs. optional parameters** — Java does not support default parameter values. Use overloading or the Builder pattern for optional arguments.
- **`void` vs. returning a value** — methods that produce a result should return it; avoid printing inside utility methods, which makes them hard to test.

---

Control flow and well-named methods are the building blocks of every Java application. Clean conditionals, the right loop for the job, and single-responsibility methods will make your Spring service layer straightforward to read, test, and maintain.
