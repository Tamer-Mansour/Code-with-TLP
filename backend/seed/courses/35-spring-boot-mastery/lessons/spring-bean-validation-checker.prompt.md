# Bean Validation Rule Checker

Jakarta Bean Validation applies constraint annotations to fields. Simulate a validation engine.

Read **N** field validation rules, each on a line as:
```
fieldName constraint value
```
where `constraint` is one of:
- `NOT_BLANK` — value must not be blank (the `value` column is `-`, ignored)
- `MIN int` — numeric value must be >= int
- `MAX int` — numeric value must be <= int
- `SIZE_MIN int` — string length must be >= int
- `SIZE_MAX int` — string length must be <= int

Multiple rules may reference the same field (e.g., both `SIZE_MIN` and `SIZE_MAX` on `username`).

Then read **T** test objects. Each test object consists of one line per **unique field** seen in the rules (in first-seen order):
```
fieldName fieldValue
```
If `fieldValue` is absent (the line contains only `fieldName`), treat it as an empty string.

For each test object, print `VALID` if all constraints pass, or list each failing rule as:
```
fieldName: CONSTRAINT violated
```
one per line, in the **order the rules were defined**.

## Input format

```
N
fieldName constraint value
...
T
fieldName fieldValue      <- one line per unique field, repeated for each test object
...
```

## Output format

`VALID` or one `fieldName: CONSTRAINT violated` line per failing rule.

## Example

**Input:**
```
4
username NOT_BLANK -
username SIZE_MIN 3
username SIZE_MAX 20
age MIN 18
3
username alice
age 25
username ab
age 15
username
age 20
```

**Output:**
```
VALID
username: SIZE_MIN violated
age: MIN violated
username: NOT_BLANK violated
username: SIZE_MIN violated
```
