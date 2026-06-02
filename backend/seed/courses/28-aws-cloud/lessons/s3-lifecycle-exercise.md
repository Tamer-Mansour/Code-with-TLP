# Exercise: S3 Storage Class Cost Calculator

Given a set of S3 objects with their sizes and age in days, determine the monthly storage cost using AWS S3 storage class pricing rules.

Lifecycle policy rules (apply in order of priority):

- If age >= 365 days: **Glacier Deep Archive** at $0.00099 per GB
- If age >= 90 days: **Glacier Instant** at $0.004 per GB
- If age >= 30 days: **Standard-IA** at $0.0125 per GB
- Otherwise: **Standard** at $0.023 per GB

Input format:
- First line: integer N (number of objects)
- Next N lines: `size_gb age_days` (integers)

Output: total monthly cost rounded to 4 decimal places.
