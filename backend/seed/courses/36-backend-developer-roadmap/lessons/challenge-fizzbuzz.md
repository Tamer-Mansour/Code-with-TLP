# Challenge: FizzBuzz

FizzBuzz is the classic entry point for learning conditional logic and modular arithmetic in any language. The challenge tests whether you can apply multiple overlapping rules in the correct order — a skill that shows up constantly when writing business logic in real Java applications.

## What this challenge teaches

- Using the **modulo operator** (`%`) to test divisibility.
- Structuring `if / else if / else` chains so that compound conditions are checked first.
- Reading from standard input with `java.util.Scanner` and printing to standard output with `System.out.println`.

## Recommended approach

Iterate from `1` to `n` inclusive. For each number, evaluate the conditions in this order:

| Check | Condition | Output |
|-------|-----------|--------|
| 1st | `i % 15 == 0` | `FizzBuzz` |
| 2nd | `i % 3 == 0` | `Fizz` |
| 3rd | `i % 5 == 0` | `Buzz` |
| 4th | none of the above | the number itself |

The order matters: `15` is a multiple of both `3` and `5`, so the divisibility-by-15 check must come first. If you check for `3` first, numbers like `15` and `30` will incorrectly print `Fizz` instead of `FizzBuzz`.

A minimal illustrative skeleton (not the full solution):

```java
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        for (int i = 1; i <= n; i++) {
            if (i % 15 == 0) {
                System.out.println("FizzBuzz");
            } else if (i % 3 == 0) {
                // TODO: handle Fizz
            } else if (i % 5 == 0) {
                // TODO: handle Buzz
            } else {
                // TODO: print i
            }
        }
    }
}
```

## Common pitfalls

- **Wrong condition order** — checking `% 3` or `% 5` before `% 15` causes `FizzBuzz` numbers to be misclassified.
- **Off-by-one errors** — the loop must start at `1` and go up to and including `n`. A `< n` boundary will miss the last number.
- **Using `print` instead of `println`** — each result must appear on its own line. Forgetting the line break will cause all output to run together and fail every test case.
- **Parsing input as a `String`** — `sc.next()` returns a `String`; you need `sc.nextInt()` (or `Integer.parseInt(sc.next())`) to get the numeric value for the loop bound.

## How input/output works

The grader passes a single integer `n` on standard input. Your program must write exactly `n` lines to standard output — one per number in the range `[1, n]` — with no trailing blank line. The grader performs an exact line-by-line comparison, so spacing and capitalisation must match precisely (`Fizz`, `Buzz`, `FizzBuzz` — capital first letter, rest lowercase).

## Before you submit

- [ ] The divisibility-by-15 branch is checked before the individual `% 3` and `% 5` branches.
- [ ] The loop range is `1` to `n` inclusive.
- [ ] Each value is printed on its own line using `System.out.println`.
- [ ] The words are spelled exactly: `Fizz`, `Buzz`, `FizzBuzz` (no extra spaces or punctuation).
- [ ] Your program compiles cleanly with `javac` under Java 17.
