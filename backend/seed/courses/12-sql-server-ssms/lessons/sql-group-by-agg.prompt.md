# GROUP BY Aggregation

## Problem

You are given **N** sales records. Each record contains a region name and an integer sale amount, separated by a comma.

Compute the **total sales amount per region**. Output each region and its total, separated by a comma, **sorted alphabetically by region name**.

This mirrors the SQL query:
```sql
SELECT   region, SUM(amount) AS total_sales
FROM     dbo.sales
GROUP BY region
ORDER BY region;
```

## Input Format

- Line 1: integer `N` — the number of sales records
- Next `N` lines: `region,amount` where `amount` is a non-negative integer

## Output Format

One line per unique region: `region,total`, sorted alphabetically by region (case-sensitive, standard string sort).

## Constraints

- `1 <= N <= 2000`
- Region names are non-empty strings with no commas
- Amounts are non-negative integers up to `1,000,000`
- At least one record is guaranteed

## Example

**Input:**
```
6
North,200
South,150
North,300
East,100
South,250
East,400
```

**Output:**
```
East,500
North,500
South,400
```

East has `100 + 400 = 500`, North has `200 + 300 = 500`, South has `150 + 250 = 400`. Output is sorted alphabetically: East, North, South.
