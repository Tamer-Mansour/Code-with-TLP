# Code Smell Detector: Long Method Line Counter

The **Long Method** code smell occurs when a function grows too large to understand easily. Martin Fowler defines this as a method exceeding ~10–20 lines of actual code.

Given the source code of a Python file as stdin, count and report:

1. For each function definition, print its name and body line count.
2. At the end, print how many functions are "long" (body line count > 10).

**Counting rules:**
- A function definition line starts with `def ` (after stripping leading whitespace) and ends with `:`.
- Body lines are non-blank, non-comment lines indented *more* than the `def` line.
- Blank lines and comment-only lines (`#`) are **not** counted in the body.

## Input Format

Raw Python source code terminated by EOF (no count prefix line).

## Output Format

```
name: N lines
...
Long methods: M
```

## Example

**Input:**
```
def add(a, b):
    return a + b

def process(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item)
        elif item == 0:
            result.append(0)
        else:
            result.append(-item)
    result.sort()
    return result
```

**Output:**
```
add: 1 lines
process: 10 lines
Long methods: 0
```
