# Build a .gitignore Matcher

## Problem

Given a list of `.gitignore` patterns followed by a blank line separator and then a list of file paths, determine which files would be **IGNORED** by Git.

**Pattern rules (simplified):**
- Lines starting with `#` are comments — ignore them
- Blank lines in the pattern section are ignored
- A pattern starting with `*.` (e.g., `*.pyc`) matches any file whose name **ends with** that extension (e.g., `.pyc`)
- Any other pattern matches if the **basename** of the path equals the pattern, OR if the **full path** equals the pattern

Print each ignored file path on its own line, in the order they appeared in the input.

## Input

```
<pattern or comment>
...
                   <- blank line separator
<filepath>
...
```

Input ends at EOF. The blank line separates the pattern section from the file list.

## Output

One ignored filepath per line, in order.

## Example

**Input:**
```
# Python cache
*.pyc
*.log
__pycache__
.env

src/main.py
src/app.pyc
logs/error.log
src/__pycache__
README.md
.env
build/output.log
```

**Output:**
```
src/app.pyc
logs/error.log
src/__pycache__
.env
build/output.log
```

## Constraints

- At most 100 patterns and 1000 file paths
- File paths use forward slashes as separators
- Pattern list is separated from file list by exactly one blank line
