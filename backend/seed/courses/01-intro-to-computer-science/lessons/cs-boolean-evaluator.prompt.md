# Boolean Expression Evaluator

Write a program that reads Boolean expressions from standard input, one per line until EOF, and prints `True` or `False` for each.

## Input format

Each line is one of:
- `NOT <operand>` — unary NOT
- `<operand> AND <operand>` — logical AND
- `<operand> OR <operand>` — logical OR
- `<operand> XOR <operand>` — exclusive OR

Where `<operand>` is either `0` (False) or `1` (True).

## Output format

Print `True` or `False` (capitalised exactly as shown) on its own line for each input expression, in the same order.

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
