# LINQ-style Aggregation

Simulate a LINQ pipeline in Python:

```csharp
var result = items
    .GroupBy(i => i.Category)
    .Select(g => new { Cat = g.Key, Avg = g.Average(x => x.Value) })
    .OrderByDescending(x => x.Avg)
    .ThenBy(x => x.Cat);
```

See the prompt for the I/O contract.
