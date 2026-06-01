# Group and Sum (Aggregation Simulation)

Implement the equivalent of:

```javascript
db.sales.aggregate([
  { $group: { _id: "$category", total: { $sum: "$amount" } } },
  { $sort:  { total: -1, _id: 1 } }
]);
```

## Input

```
N
<category,amount>
<category,amount>
... N lines
```

- `N` is the number of records (1 ≤ N ≤ 10000).
- Each line has a category (non-empty string, no commas) and an integer `amount`.

## Output

For each distinct category, sum its `amount` values. Print them as `category,total`, sorted by:

1. `total` descending,
2. `category` ascending (lexicographic).

## Example

Input:

```
5
books,10
toys,5
books,20
toys,15
books,7
```

Output:

```
books,37
toys,20
```

If amounts tie, alphabetical order wins:

Input:

```
4
z,10
a,10
b,5
c,5
```

Output:

```
a,10
z,10
b,5
c,5
```
