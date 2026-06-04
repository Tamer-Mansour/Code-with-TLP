# Log Level Filter and Counter

Filter syslog-style log messages by RFC 5424 severity level and count matches.

## What you'll practice

- RFC 5424 severity levels and their numeric ordering
- Filtering structured text by a threshold condition
- Counting and summarizing results

## Key concept

Syslog severity runs **numerically backwards** from human intuition: `EMERG=0` is the most severe, `DEBUG=7` is the least. When filtering "at or above WARNING", you keep everything with a level number **less than or equal to** WARNING's number (4). Confusing this direction is a very common mistake when writing log-processing scripts.

## Task

Given `N` log lines in `LEVEL: message` format and a threshold level name, print all lines whose severity is at least as severe as the threshold, then print a `Matched: X of N` summary.

See the problem statement for the full severity table and examples.
