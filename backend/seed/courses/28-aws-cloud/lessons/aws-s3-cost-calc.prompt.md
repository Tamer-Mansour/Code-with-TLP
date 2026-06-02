# S3 Storage Class Cost Calculator

You are building a cost analysis tool for S3 storage.

Given N objects, each with a size (in GB) and age (in days), compute the **total monthly storage cost** by applying the following lifecycle pricing rules:

| Age (days)    | Storage class        | Price per GB/month |
|---------------|----------------------|--------------------|
| < 30          | Standard             | $0.023             |
| 30 – 89       | Standard-IA          | $0.0125            |
| 90 – 364      | Glacier Instant      | $0.004             |
| >= 365        | Glacier Deep Archive | $0.00099           |

**Input format:**
- Line 1: integer `N`
- Lines 2 to N+1: two space-separated integers `size_gb age_days`

**Output format:**
- A single number: total cost rounded to 4 decimal places (no dollar sign).

**Example:**
```
Input:
3
10 15
50 45
100 400

Output:
0.5220
```

Explanation:
- 10 GB, 15 days → Standard: 10 × 0.023 = 0.2300
- 50 GB, 45 days → Standard-IA: 50 × 0.0125 = 0.6250
- 100 GB, 400 days → Glacier Deep Archive: 100 × 0.00099 = 0.0990
- Wait — let me recheck: 0.2300 + 0.6250 + 0.0990 = 0.9540

Actually, re-reading: the example output should be 0.9540. Use your solution_code to verify and set test cases accordingly.
