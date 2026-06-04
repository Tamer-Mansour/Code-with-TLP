# Log Level Filter and Counter

Simulate a syslog severity filter: keep only messages at or above a given severity threshold, then report how many matched.

## Background

The **RFC 5424** syslog standard defines eight severity levels numbered 0 (most severe) through 7 (least severe):

| Level   | Number | Meaning                    |
|---------|--------|----------------------------|
| EMERG   | 0      | System is unusable         |
| ALERT   | 1      | Action must be taken immediately |
| CRIT    | 2      | Critical conditions        |
| ERR     | 3      | Error conditions           |
| WARNING | 4      | Warning conditions         |
| NOTICE  | 5      | Normal but significant     |
| INFO    | 6      | Informational              |
| DEBUG   | 7      | Debug-level messages       |

"At or above the threshold" means **numerically less than or equal to** the threshold's number — i.e., as severe as or more severe than the threshold.

## Input

- First line: integer `N` — number of log lines.
- Next `N` lines: each in the format `LEVEL: message` where `LEVEL` is one of the eight names above.
- Last line: the threshold level name (e.g., `WARNING`).

## Output

1. All matching log lines (those whose severity <= threshold severity number), in their original order.
2. A summary line: `Matched: X of N`

## Examples

**Example 1**

Input:
```
5
ERR: disk full
INFO: service started
CRIT: kernel panic
DEBUG: connection trace
WARNING: high load
WARNING
```

Output:
```
ERR: disk full
CRIT: kernel panic
WARNING: high load
Matched: 3 of 5
```

Explanation: WARNING has level 4. ERR=3, CRIT=2, WARNING=4 are all <= 4. INFO=6 and DEBUG=7 are excluded.

**Example 2**

Input:
```
3
DEBUG: verbose trace
EMERG: power failure
ALERT: memory exhausted
CRIT
```

Output:
```
EMERG: power failure
ALERT: memory exhausted
Matched: 2 of 3
```

**Example 3**

Input:
```
4
NOTICE: config reloaded
INFO: user logged in
DEBUG: query took 2ms
ERR: timeout
DEBUG
```

Output:
```
NOTICE: config reloaded
INFO: user logged in
DEBUG: query took 2ms
ERR: timeout
Matched: 4 of 4
```

**Example 4**

Input:
```
3
INFO: startup complete
DEBUG: init sequence
NOTICE: ready
EMERG
```

Output:
```
Matched: 0 of 3
```

## Notes

- Log lines are always well-formed with a valid level name.
- The threshold is always a valid level name.
- Preserve the original order of matching lines.
- The summary line is always printed, even when zero lines match.
