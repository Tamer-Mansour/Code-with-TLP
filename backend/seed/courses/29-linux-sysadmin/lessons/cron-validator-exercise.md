# Cron Expression Validator

Validate standard five-field cron expressions against correct field ranges.

## What you'll practice

- Cron syntax: five fields, their meanings, and valid ranges
- Parsing structured text input
- Input validation logic with multiple constraints

## Key concept

A cron expression that appears to "work" but has an out-of-range value may still be accepted by some cron implementations while silently behaving unexpectedly on others. Understanding the exact valid ranges for each field prevents subtle scheduling bugs in production.

The five fields are `minute hour day-of-month month day-of-week`. Fields can be `*` (wildcard), a single integer, or a range `start-end`. Step values such as `*/5` are NOT part of this simplified spec.

## Task

Read `N` cron expressions and for each one print `VALID` or `INVALID`.

See the problem statement for the full field-range table and input/output specification.
