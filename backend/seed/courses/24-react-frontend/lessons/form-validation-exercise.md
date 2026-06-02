# Exercise: Form Validation Rules

Practice implementing form validation logic by simulating a validator that processes field rules and input values.

Given a series of validation checks, determine which fields pass or fail.

Each line of input has the format: `FIELD VALUE RULE PARAM`

Rules:
- `required` — field must be non-empty (PARAM is ignored, use `_`)
- `minlen N` — value length must be >= N
- `maxlen N` — value length must be <= N
- `regex PATTERN` — value must match the regex pattern exactly

Output one line per check: `FIELD: PASS` or `FIELD: FAIL`
