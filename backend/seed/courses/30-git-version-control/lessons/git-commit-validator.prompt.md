# Commit Message Validator

## Problem

Many teams enforce commit message conventions using Git hooks or CI checks. Write a program that reads commit messages (one per line) and validates each one against these rules:

1. The subject line must be **72 characters or fewer**
2. The subject line must **not end with a period**
3. The subject line must **start with a capital letter**

For each non-empty message, print `OK` if it passes all rules, or print the **first** rule violation as:

```
ERROR: <reason>
```

Check rules in the order listed above (length first, then period, then capitalization).

## Input

One commit message subject per line. Input ends at EOF. Skip empty lines.

## Output

One result per non-empty input line.

## Example

**Input:**
```
Add user authentication module
fix login bug.
add new feature for the dashboard that handles all the user interactions and navigation throughout the entire application
Update README
refactored database connection pooling logic
```

**Output:**
```
OK
ERROR: subject line must not end with a period
ERROR: subject line must be 72 characters or fewer
OK
ERROR: subject line must start with a capital letter
```

## Constraints

- At most 1000 messages
- Each message is a single line of text
- A message that both exceeds 72 chars AND ends with a period should report the length error (checked first)
