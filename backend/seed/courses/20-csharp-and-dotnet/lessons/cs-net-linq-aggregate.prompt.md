# GroupBy Average

Implement the equivalent of this LINQ query:

```csharp
items
  .GroupBy(i => i.Cat)
  .Select(g => new { Cat = g.Key, Avg = g.Average(x => x.Value) })
  .OrderByDescending(x => x.Avg)
  .ThenBy(x => x.Cat);
```

## Input

```
N
<cat,value>
... N lines
```

- `N` is the number of records (1 ≤ N ≤ 10000).
- Each line has a category (no commas) and an integer value.

## Output

For each distinct category, print `category average`, where `average` is the arithmetic mean rounded to two decimals, **printed as an integer if exact**.

Sort by average descending, then category ascending.

## Examples

Input:

```
5
A,10
B,20
A,30
B,40
C,50
```

Output:

```
C 50
B 30
A 20
```

Input:

```
3
x,1
x,2
x,4
```

Output:

```
x 2.33
```

## Notes

- Averages with no fractional part: print as integer (`20`, not `20.00`).
- Averages with fraction: print two decimal places (`2.33`).
- Tie on average: alphabetic order ascending.
