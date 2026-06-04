# S3 Storage Class Cost Calculator

You are building a cost analysis tool for an S3 storage audit. Given a list of S3 objects with their sizes and current storage classes, calculate the total monthly storage cost.

## Storage Class Prices (per GB per month)

| Storage Class  | Price ($/GB/month) |
|----------------|--------------------|
| STANDARD       | $0.023             |
| STANDARD_IA    | $0.0125            |
| GLACIER        | $0.004             |
| DEEP_ARCHIVE   | $0.00099           |

## Input Format

- Line 1: integer `N` — number of objects
- Lines 2 to N+1: `<size_gb> <storage_class>` — size as a positive integer (GB), storage class is exactly one of the four values above

## Output Format

A single number: total monthly cost rounded to **4 decimal places** (no dollar sign).

## Example

```
Input:
5
100 STANDARD
500 STANDARD_IA
1000 GLACIER
2000 DEEP_ARCHIVE
50 STANDARD

Output:
15.6800
```

Explanation:
- 100 GB × $0.023 = $2.3000
- 500 GB × $0.0125 = $6.2500
- 1000 GB × $0.004 = $4.0000
- 2000 GB × $0.00099 = $1.9800
- 50 GB × $0.023 = $1.1500
- Total = $15.6800

## Constraints

- 1 ≤ N ≤ 1000
- 1 ≤ size_gb ≤ 10000 (integer)
- Storage class is always one of: `STANDARD`, `STANDARD_IA`, `GLACIER`, `DEEP_ARCHIVE`
