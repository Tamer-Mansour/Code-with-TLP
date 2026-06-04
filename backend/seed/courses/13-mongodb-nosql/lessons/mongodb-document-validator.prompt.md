# Document Validator

MongoDB documents are flexible by default, but real applications need required fields. Write a program that validates documents read from stdin.

## Input Format

A sequence of records separated by `---` on its own line. Each record consists of `key:value` lines (one pair per line). Read until EOF.

## Output Format

For each record (in order), print one line:

- `VALID` — if the record contains all three required fields: `name`, `age`, and `email`.
- `MISSING: <fields>` — listing the absent required fields in alphabetical order, comma-separated (no spaces after commas).

## Example

**Input:**
```
name:Alice
age:30
email:alice@example.com
---
name:Bob
email:bob@example.com
---
age:25
```

**Output:**
```
VALID
MISSING: age
MISSING: email,name
```

## Notes

- A record ends when `---` is encountered or at EOF.
- A field is "present" if its key appears at least once in the record (values are irrelevant for validation).
- The required fields are exactly: `name`, `age`, `email`.
- Missing fields must be listed alphabetically: `age` before `email` before `name`.
- Lines that do not contain `:` should be ignored.
