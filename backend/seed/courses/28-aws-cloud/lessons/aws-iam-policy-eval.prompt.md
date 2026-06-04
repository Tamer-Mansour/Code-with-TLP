# IAM Policy Evaluator

AWS IAM uses a specific evaluation logic when determining whether an action is allowed or denied. Your task is to simulate that logic.

## Evaluation Rules

1. If any statement explicitly **Deny**s the action, the result is `DENY` (explicit deny wins).
2. If no explicit deny exists but at least one statement explicitly **Allow**s the action, the result is `ALLOW`.
3. Otherwise (no match at all), the result is `DENY` (implicit deny).

Action patterns support a wildcard `*` **only at the end** — for example, `s3:*` matches any action that starts with `s3:`, and `*` alone matches everything.

## Input Format

- Line 1: integer `N` — number of policy statements
- Lines 2 to N+1: two space-separated tokens `<Effect> <Action>` where Effect is `Allow` or `Deny`
- Last line: the action to evaluate

## Output Format

A single line: `ALLOW` or `DENY`

## Example

```
Input:
4
Allow s3:GetObject
Allow s3:PutObject
Deny s3:DeleteObject
Allow ec2:DescribeInstances
s3:DeleteObject

Output:
DENY
```

Explanation: `s3:DeleteObject` is explicitly denied, so the result is `DENY` regardless of any allow statements.

## Another Example

```
Input:
3
Allow s3:*
Allow ec2:DescribeInstances
Deny ec2:TerminateInstances
s3:GetObject

Output:
ALLOW
```

Explanation: `s3:*` matches `s3:GetObject` with an Allow. No explicit Deny matches. Result is `ALLOW`.

## Edge Cases

- An action not covered by any statement → `DENY` (implicit deny)
- `*` matches any action
- Wildcards only appear at the end of a pattern
