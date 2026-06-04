# Cron Expression Validator

Validate cron scheduling expressions against the standard five-field crontab format.

## Background

A cron expression consists of exactly **five whitespace-separated fields** that define when a job runs:

```
minute  hour  day-of-month  month  day-of-week
```

Each field has a specific valid range. Errors in cron syntax cause jobs to silently fail or never run — validation is an important automation skill.

## Field Ranges

| Field         | Range               | Notes                        |
|---------------|---------------------|------------------------------|
| minute        | 0–59                |                              |
| hour          | 0–23                |                              |
| day-of-month  | 1–31                |                              |
| month         | 1–12                |                              |
| day-of-week   | 0–7                 | 0 and 7 both mean Sunday     |

## Allowed Field Values (simplified spec for this problem)

Each field may be:

- `*` — any value (always valid)
- A single integer — must be within the field's range
- A range `start-end` — both endpoints must be within range and `start <= end`

**Step values like `*/5` or `1-5/2` are NOT valid** in this simplified spec and must be marked `INVALID`.

## Input

- First line: integer `N`.
- Next `N` lines: one cron expression per line (five space-separated tokens).

## Output

For each expression, print `VALID` or `INVALID` on its own line.

## Examples

**Example 1**

Input:
```
4
0 2 * * 0
60 25 1 1 1
*/5 * * * *
30 8 15 13 3
```

Output:
```
VALID
INVALID
INVALID
INVALID
```

Explanation:
- `0 2 * * 0` — minute=0, hour=2, dom=*, month=*, dow=0 (Sunday). All valid.
- `60 25 1 1 1` — minute=60 (out of range 0-59), hour=25 (out of range 0-23). INVALID.
- `*/5 * * * *` — step syntax is not allowed in this spec. INVALID.
- `30 8 15 13 3` — month=13 (out of range 1-12). INVALID.

**Example 2**

Input:
```
3
0 0 1 1 0
59 23 31 12 7
1-5 * * * *
```

Output:
```
VALID
VALID
VALID
```

**Example 3**

Input:
```
2
0 0 0 1 1
5 12 * * 8
```

Output:
```
INVALID
INVALID
```

Explanation:
- `0 0 0 1 1` — day-of-month=0 (must be 1-31). INVALID.
- `5 12 * * 8` — day-of-week=8 (must be 0-7). INVALID.

## Notes

- An expression with fewer or more than 5 fields is always INVALID.
- Empty or malformed fields are INVALID.
- Range endpoints must both be integers within the valid range.
