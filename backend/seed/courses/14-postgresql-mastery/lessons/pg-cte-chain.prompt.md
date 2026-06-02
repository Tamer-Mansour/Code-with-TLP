# JSONB-style CTE Chain Filter

You are given a list of orders. Each order is on one line with three space-separated fields:

```
customer_id  status  month
```

- `status` is either `paid` or `unpaid`
- `month` is an integer 1-12

**Step 1** — filter to only `paid` orders (simulating the first CTE).  
**Step 2** — from that result, keep only orders where `month == 6` (simulating the second CTE).  
**Step 3** — count orders per `customer_id` from the final set and print each `customer_id` and count, sorted ascending by `customer_id`, one per line in the format `customer_id count`.

## Input format

```
N
customer_id status month
... (N lines)
```

## Output format

```
customer_id count
```

One line per customer that has at least one matching order, sorted by `customer_id` ascending.

## Example

Input:
```
5
1 paid 6
2 unpaid 6
1 paid 5
3 paid 6
1 paid 6
```

Output:
```
1 2
3 1
```
