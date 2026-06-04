# Exercise: Code Smell Detector — Long Method Line Counter

One of the most common code smells is the **Long Method**: a function that has grown too large to understand easily. Martin Fowler, in *Refactoring: Improving the Design of Existing Code*, describes the Long Method as a function exceeding roughly 10–20 lines of actual code. Long methods accumulate over time as developers add "just one more thing" — each addition feels small, but the result becomes unreadable.

The fix for a Long Method is **Extract Method**: identify a coherent block of statements that does one sub-task and move it into its own well-named function. After extraction, both functions become easier to read, name, and test.

## Task

You are given the source code of a Python file as stdin. Analyze it and report:

1. For each function definition found, print its name and body line count.
2. At the end, print how many functions are "long" (body line count > 10).

**Counting rules:**
- A function definition line starts with `def ` after stripping leading whitespace and ends with `:`.
- Body lines are non-blank, non-comment lines that are indented *more* than the `def` line itself.
- Blank lines (empty or whitespace-only) and comment-only lines (stripped content starts with `#`) are **not** counted.

## Input Format

Raw Python source code, terminated by EOF (no count prefix).

## Output Format

One line per function: `name: N lines`

Then a final line: `Long methods: M`

## Example

**Input:**
```python
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

## Hints

- Track the indentation level of each `def` line using `len(line) - len(line.lstrip())`.
- A line belongs to the current function's body only if its indentation is strictly greater than the `def` line's indentation.
- When you encounter a non-blank, non-comment line at the same or lesser indentation as the `def` line, the function body has ended.
- Save the previous function's count before starting a new one.
