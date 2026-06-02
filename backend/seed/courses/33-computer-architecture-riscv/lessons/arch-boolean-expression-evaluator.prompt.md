# Boolean Expression Evaluator

## Problem Statement

Write a program that evaluates a Boolean expression given the values of variables `A`, `B`, `C`, and `D`.

Supported operators (precedence from highest to lowest):
1. `!` — NOT (unary prefix)
2. `&` — AND (binary)
3. `|` — OR (binary)

Parentheses `(` `)` override precedence.

## Input Format

```
Line 1: A Boolean expression with no spaces, using characters A B C D & | ! ( )
Line 2: Variable assignments separated by spaces in the form X=0 or X=1
        Always exactly four assignments: A=?, B=?, C=?, D=?
```

## Output Format

```
A single integer: 0 or 1
```

## Constraints

- Expression length: 1–50 characters
- Only valid characters: `A`, `B`, `C`, `D`, `&`, `|`, `!`, `(`, `)`
- Expressions are syntactically valid
- All four variables A, B, C, D are always assigned

## Sample Input 1

```
A&B|C
A=1 B=0 C=1 D=0
```

## Sample Output 1

```
1
```

**Explanation**: Operator precedence gives `(A&B)|C = (1&0)|1 = 0|1 = 1`.

## Sample Input 2

```
!A&B
A=1 B=1 C=0 D=0
```

## Sample Output 2

```
0
```

**Explanation**: `(!A)&B = (!1)&1 = 0&1 = 0`.

## Sample Input 3

```
(A|B)&(!C)
A=1 B=0 C=0 D=0
```

## Sample Output 3

```
1
```

**Explanation**: `(1|0)&(!0) = 1&1 = 1`.

## Hints

- Use recursive descent parsing: one function per precedence level.
- Substitute variable values into the expression string before parsing, or look them up during parsing.
- Handle `!` recursively: `parse_factor` calls itself when it sees `!`.
- Parentheses: on `(`, call `parse_expr()` recursively, then consume `)`.
