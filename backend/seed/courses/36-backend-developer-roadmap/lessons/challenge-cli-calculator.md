# Challenge: Command-Line Calculator

This challenge exercises the most fundamental Java I/O skill you will use throughout the course: reading structured input from `System.in`, parsing it into typed values, and writing a single result to `System.out`. Every server-side program — from REST controllers to batch jobs — follows the same read-parse-compute-emit cycle, so mastering it at the command line first keeps the focus on logic rather than framework plumbing.

## What the challenge teaches

- Using `java.util.Scanner` to tokenise a line from standard input.
- Parsing `String` tokens into `int` (or `long`) with `Integer.parseInt`.
- Dispatching on a `String` operator with a `switch` expression (Java 14+) or an `if-else` chain.
- Printing a plain integer result with `System.out.println`.

## Recommended approach

Read the entire line, split on whitespace, and treat the three tokens as `a`, `op`, and `b`.

```java
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int a  = sc.nextInt();
        String op = sc.next();
        int b  = sc.nextInt();

        int result = switch (op) {
            case "+" -> a + b;
            case "-" -> a - b;
            case "*" -> a * b;
            case "/" -> a / b;   // truncates toward zero — matches the spec
            default  -> throw new IllegalArgumentException("Unknown op: " + op);
        };

        System.out.println(result);
    }
}
```

This snippet is illustrative — your submitted solution must handle all four operators to pass every test case.

## Input / output contract

| Token | Type | Example |
|-------|------|---------|
| `a`   | `int` (may be negative) | `-10` |
| `op`  | `String`, one of `+ - * /` | `*` |
| `b`   | `int` (may be negative) | `3` |

Given input `3 + 4`, the expected output is:

```
7
```

Given input `-10 * 3`, the expected output is:

```
-30
```

## Common pitfalls

- **Reading with `nextLine()` after `nextInt()`** — `nextLine()` consumes the leftover newline and returns an empty string. Use `nextInt()` / `next()` consistently, or call `sc.nextLine()` once to flush before switching modes.
- **Integer overflow** — the operands are `int`-sized, but multiplying two large values can overflow silently. If the grader uses values near `Integer.MAX_VALUE`, promote to `long` before the operation.
- **`"*"` in a shell** — when running manually, wrap the expression in quotes to prevent glob expansion: `echo "6 * 7" | java Main`. This is a shell concern only; your Java code needs no changes.
- **Missing `default` branch** — the switch must compile without warning; always include a `default` or ensure exhaustiveness.
- **Extra whitespace in output** — print only the integer, no spaces or extra newlines.

## Before you submit

- [ ] My program compiles without warnings with `javac Main.java`.
- [ ] It produces the correct result for all four operators (`+`, `-`, `*`, `/`).
- [ ] It handles negative operands (e.g., `-5 / 2` → `-2`).
- [ ] It prints exactly one line with no trailing spaces.
- [ ] I have not hard-coded a specific test case — the solution reads from `System.in`.
