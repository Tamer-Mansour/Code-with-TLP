# Form Validation Rules

You are implementing a simple form validator.

**Input format:** Each line contains four space-separated tokens: `FIELD VALUE RULE PARAM`

**Rules:**
- `required _` — the VALUE must be non-empty (PARAM is always `_` for this rule)
- `minlen N` — `len(VALUE) >= N`
- `maxlen N` — `len(VALUE) <= N`
- `regex PATTERN` — VALUE must fully match the regex PATTERN (use `re.fullmatch`)

**Output:** For each input line, print `FIELD: PASS` or `FIELD: FAIL` (one line per check).

**Example:**

Input:
```
email alice@example.com required _
name  _ required _
pass  secret123 minlen 8
pass  hi maxlen 3
```

Output:
```
email: PASS
name: FAIL
pass: PASS
pass: PASS
```
