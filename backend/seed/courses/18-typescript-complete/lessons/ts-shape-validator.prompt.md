# Required-Fields Validator

Given a list of required field names and a series of JSON documents, validate each document.

## Input

```
<comma-separated required fields>
N
<json doc 1>
<json doc 2>
... N docs
```

- Line 1: required fields, comma-separated, no spaces (e.g. `name,email`).
- Line 2: number of documents N (0 ≤ N ≤ 1000).
- Following N lines: each line is one JSON object.

## Output

For each document, print one line:

- `OK` — every required field is present (extra fields are fine).
- `MISSING <a,b,c>` — these required fields are absent (preserve required-list order).
- `INVALID` — the line is not valid JSON.

## Example

Input:

```
name,email
3
{"name":"Alice","email":"a@x"}
{"name":"Bob"}
{"email":"c@x"}
```

Output:

```
OK
MISSING email
MISSING name
```

## Notes

- The presence check only looks at top-level keys.
- A field is "present" if the key exists in the object, regardless of its value (even `null` counts).
