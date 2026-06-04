# Exercise: Grade Classifier with Exception Handling

`NumberFormatException` is one of the most common runtime errors in Java. It is thrown by `Integer.parseInt()` when the input string is not a valid integer. This exercise practises the try-catch pattern that every Java developer uses daily.

## Java pattern

```java
try {
    int grade = Integer.parseInt(rawInput.trim());
    if (grade < 0 || grade > 100) {
        System.out.println("Out of range");
    } else if (grade >= 90) {
        System.out.println("A");
    } else if (grade >= 80) {
        System.out.println("B");
    } else if (grade >= 70) {
        System.out.println("C");
    } else if (grade >= 60) {
        System.out.println("D");
    } else {
        System.out.println("F");
    }
} catch (NumberFormatException e) {
    System.out.println("Invalid input");
}
```

Key points:
- The `catch (NumberFormatException e)` block handles the case where the string cannot be parsed as an integer.
- Range validation (`< 0 || > 100`) is done *inside* the try block, after the parse succeeds.
- The order of `else if` branches matters: check the highest grade first.

## Checked vs unchecked

`NumberFormatException` is an **unchecked** exception (a subclass of `RuntimeException`). You are not required to declare it in a `throws` clause, but catching it is good defensive practice when you receive user input. Unchecked exceptions represent programming errors or invalid input, while checked exceptions (like `IOException`) represent recoverable external conditions.

## Problem statement

Read `N` on the first line. Then read `N` lines, each containing a string. For each string:

- If it is not a valid integer: print `Invalid input`.
- If it is a valid integer but outside `[0, 100]`: print `Out of range`.
- Otherwise print the letter grade: `A` (90-100), `B` (80-89), `C` (70-79), `D` (60-69), `F` (0-59).

### Example

Input:
```
6
95
82
abc
55
-5
101
```

Output:
```
A
B
Invalid input
F
Out of range
Out of range
```

## Further reading

- David J. Eck, *Introduction to Programming Using Java* (9th ed.) — Chapter 8: Correctness, Robustness, Efficiency: https://math.hws.edu/javanotes/
- *Think Java* (2nd ed.) — Chapter 12: Exceptions: https://greenteapress.com/wp/think-java-2e/
