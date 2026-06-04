# Exercise: Variable Types and Arithmetic

Java's integer division is a common source of bugs for newcomers. When both operands of `/` are `int` values, the result is also an `int` — the fractional part is discarded (truncated toward zero), not rounded.

```java
int a = 17, b = 5;
System.out.println(a / b);   // 3, not 3.4
System.out.println(a % b);   // 2  (remainder)
```

To get a floating-point result, cast at least one operand to `double`:

```java
double result = (double) a / b;  // 3.4
```

## What you'll practise

- Reading `int` values with `Scanner`
- The four basic arithmetic operators on integers
- Labelled output with `System.out.printf` or string concatenation
- Understanding integer division truncation

## Problem statement

Read two integers from stdin, one per line. Print their **sum**, **difference**, **product**, and **integer quotient** (floor division), each on a separate line prefixed with its label and a colon.

### Example

Input:
```
17
5
```

Output:
```
Sum: 22
Difference: 12
Product: 85
Quotient: 3
```

## Further reading

- David J. Eck, *Introduction to Programming Using Java* (9th ed.) — Chapter 2: Basic Java, section on types and operators: https://math.hws.edu/javanotes/
- Allen B. Downey & Chris Mayfield, *Think Java* (2nd ed.) — Chapter 1 covers variables and arithmetic: https://greenteapress.com/wp/think-java-2e/
