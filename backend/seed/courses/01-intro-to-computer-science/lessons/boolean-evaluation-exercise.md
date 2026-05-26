# Exercise: Boolean Expression Evaluator

Practice Boolean logic by building an expression evaluator.

Your program reads Boolean expressions from standard input (one per line) and prints the result (`True` or `False`) for each.

Expressions use these elements:
- Operands: `1` (True) or `0` (False)
- Operators: `AND`, `OR`, `NOT`, `XOR`
- `NOT` is a unary prefix operator applied to a single operand: `NOT 1`
- All other operators are binary: `1 AND 0`
- No parentheses; expressions are always in one of these exact forms:
  - `NOT <operand>`
  - `<operand> AND <operand>`
  - `<operand> OR <operand>`
  - `<operand> XOR <operand>`

Read until EOF and print one result per line.

## Example

**Input:**
```
1 AND 0
1 OR 0
NOT 1
0 XOR 0
1 XOR 1
NOT 0
```

**Output:**
```
False
True
False
False
False
True
```
