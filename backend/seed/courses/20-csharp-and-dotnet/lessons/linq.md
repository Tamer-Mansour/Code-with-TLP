# LINQ

LINQ — **Language Integrated Query** — is C#'s answer to functional collection processing. It works on arrays, lists, dictionaries, databases (Entity Framework), and XML.

## Method syntax

```csharp
using System.Linq;

var nums = new[] { 1, 2, 3, 4, 5, 6 };

var evens = nums.Where(n => n % 2 == 0);
var squared = nums.Select(n => n * n);
var total = nums.Sum();
var first = nums.First(n => n > 3);          // throws if none
var firstOrNull = nums.FirstOrDefault(n => n > 100);   // null/0 if none
```

## Query syntax

The SQL-looking form:

```csharp
var result =
    from u in users
    where u.IsActive
    orderby u.Name
    select new { u.Id, u.Name };
```

Compiles to method syntax. Use either; modern code leans on method syntax.

## Common operators

| Method          | What it does                                |
|-----------------|---------------------------------------------|
| `Where`         | filter                                      |
| `Select`        | transform                                   |
| `SelectMany`    | flat-map                                    |
| `OrderBy / ThenBy` | sort                                     |
| `GroupBy`       | group                                       |
| `Distinct`      | unique                                      |
| `Take` / `Skip` | pagination                                  |
| `First` / `Last` / `Single` | extract one                       |
| `Any` / `All`   | predicates over the whole collection        |
| `Count`         | count, optionally with predicate            |
| `Sum`/`Average`/`Min`/`Max` | aggregates                      |
| `Aggregate`     | custom reduce                               |
| `ToList`/`ToArray`/`ToDictionary` | materialize             |

## GroupBy

```csharp
var byCountry = users
    .GroupBy(u => u.Country)
    .Select(g => new { Country = g.Key, Count = g.Count() });
```

`g` is a group — iterable, with `Key` and the matching items.

## Join

```csharp
var orders = users
    .Join(orderTable,
          u => u.Id,
          o => o.UserId,
          (u, o) => new { u.Name, o.Total });
```

## Deferred execution

Most operators are **lazy** — they don't execute until you iterate (`foreach`, `ToList`, `Count`).

```csharp
var q = nums.Where(n => { Console.WriteLine($"checking {n}"); return n > 2; });
// nothing printed yet
foreach (var x in q) { ... }            // now it runs
```

Multiple iterations re-run the pipeline. Cache with `.ToList()` if that matters.

## LINQ to SQL (Entity Framework)

The same syntax queries a database:

```csharp
var topCustomers = db.Customers
    .Where(c => c.Country == "US")
    .OrderByDescending(c => c.Spend)
    .Take(10)
    .Select(c => new { c.Id, c.Name })
    .ToList();
```

EF translates this to SQL. Inspect with `db.Database.Log = Console.WriteLine`.

## Performance notes

- Each LINQ operator allocates an iterator. Hot loops can prefer a plain `foreach`.
- `ToList()` materializes — sometimes premature, sometimes essential.
- `Count()` on a query is O(n) unless the source is a `List`/`Collection`; use `Any()` to check non-emptiness.
- `Where(x => p(x)).First()` is the same as `First(p)` — same allocations either way.

## A real-world combo

```csharp
var topPaidCustomers = orders
    .Where(o => o.Status == "paid")
    .GroupBy(o => o.CustomerId)
    .Select(g => new { CustomerId = g.Key, Total = g.Sum(o => o.Amount) })
    .OrderByDescending(x => x.Total)
    .Take(10)
    .ToList();
```

Three SQL-style operations (filter + group + sort) in five readable lines.
