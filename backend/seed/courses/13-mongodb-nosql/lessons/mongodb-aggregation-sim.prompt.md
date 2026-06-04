# Aggregation Pipeline Simulator

Simulate a simplified two-stage MongoDB aggregation pipeline.

## Input Format

```
N
category1:value1
category2:value2
...  (N records total)
$match category=<X>
$group
```

- Line 1: integer N, the number of records.
- Next N lines: each is `category:value` where value is a non-negative integer.
- Then: a `$match` stage line of the form `$match category=<X>`.
- Then: a `$group` stage line (the literal string `$group`).

## Output Format

Two lines:

```
count:<N>
sum:<total>
```

Where `N` is the number of records whose category equals `X`, and `total` is the sum of their values. If no records match, print `count:0` and `sum:0`.

## Example

**Input:**
```
5
fruit:10
vegetable:20
fruit:30
fruit:5
vegetable:15
$match category=fruit
$group
```

**Output:**
```
count:3
sum:45
```

## Notes

- Category comparison is case-sensitive.
- Values are always non-negative integers.
- There is always exactly one `$match` stage and one `$group` stage after the records.
