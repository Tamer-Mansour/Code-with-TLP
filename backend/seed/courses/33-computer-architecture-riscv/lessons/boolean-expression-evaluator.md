# Exercise: Evaluate a Boolean Expression

Boolean algebra is not just theoretical — logic simulators, hardware synthesis tools, and formal verification engines all need to evaluate Boolean expressions programmatically. In this exercise you will implement a simple Boolean expression evaluator.

## What You Will Implement

Write a program that reads a Boolean expression using variables `A`, `B`, `C`, and `D` (each 0 or 1), along with the values of those variables, and prints the result of evaluating the expression.

Supported operators (in order of precedence, highest first):
1. `!` — NOT (unary prefix)
2. `&` — AND
3. `|` — OR

Parentheses `(` `)` may be used to override precedence.

Variables are single uppercase letters: `A`, `B`, `C`, `D`.

## Input Format

```
Line 1: The Boolean expression (no spaces)
Line 2: Space-separated variable assignments, e.g. A=1 B=0 C=1 D=1
```

## Output Format

A single line: `0` or `1`

## Example

Input:
```
A&B|C
A=1 B=0 C=1 D=0
```

Output:
```
1
```

Explanation: `A&B` = 1&0 = 0, then `0|C` = 0|1 = 1.

## Constraints

- Expression length: 1–50 characters
- Only valid characters appear: `A B C D & | ! ( )`
- At least one variable will appear in the expression
- Assignments will always include A, B, C, and D

## Skill Focus

This exercise reinforces understanding of operator precedence in Boolean logic — the same precedence hierarchy that determines evaluation order in hardware synthesis tools and HDL compilers. A candidate who can write this evaluator understands how `A&B|C` means `(A&B)|C`, not `A&(B|C)`.
