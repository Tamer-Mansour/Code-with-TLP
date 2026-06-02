# Arrays and Collections in C#

The .NET BCL (Base Class Library) ships a rich set of collection types. Choosing the right one affects both readability and performance.

## Arrays

Fixed-size, zero-indexed, stored contiguously in memory:

```csharp
int[] scores = new int[5];           // all zeros
int[] primes = { 2, 3, 5, 7, 11 };  // array initializer

Console.WriteLine(primes.Length);    // 5
Console.WriteLine(primes[0]);        // 2
```

Multi-dimensional:

```csharp
int[,] matrix = new int[3, 4];       // 3 rows, 4 cols
int[][] jagged = new int[3][];       // rows of different lengths
```

## List\<T\>

The go-to general-purpose collection — dynamic size, O(1) amortized append:

```csharp
var names = new List<string> { "Alice", "Bob" };
names.Add("Carol");
names.Remove("Bob");
names.Insert(0, "Zara");             // insert at index

Console.WriteLine(names.Count);     // 3
Console.WriteLine(names[0]);        // Zara
```

## Dictionary\<TKey, TValue\>

Hash map — O(1) average lookup:

```csharp
var capitals = new Dictionary<string, string>
{
    ["France"]  = "Paris",
    ["Germany"] = "Berlin",
};

capitals["Japan"] = "Tokyo";

if (capitals.TryGetValue("France", out string? city))
    Console.WriteLine(city);        // Paris

foreach (var (country, capital) in capitals)
    Console.WriteLine($"{country}: {capital}");
```

Always prefer `TryGetValue` over the indexer when the key might be absent — the indexer throws `KeyNotFoundException`.

## HashSet\<T\>

Unique elements, O(1) add/contains:

```csharp
var seen = new HashSet<int>();
seen.Add(1);
seen.Add(2);
seen.Add(1);                         // ignored — duplicate
Console.WriteLine(seen.Count);       // 2
Console.WriteLine(seen.Contains(2)); // True
```

## Queue\<T\> and Stack\<T\>

```csharp
var queue = new Queue<string>();
queue.Enqueue("first");
queue.Enqueue("second");
Console.WriteLine(queue.Dequeue());  // first (FIFO)

var stack = new Stack<int>();
stack.Push(10);
stack.Push(20);
Console.WriteLine(stack.Pop());      // 20 (LIFO)
```

## IEnumerable\<T\> — the common interface

All collections implement `IEnumerable<T>`, so they work with `foreach` and LINQ:

```csharp
IEnumerable<int> Source(IEnumerable<int> items) =>
    items.Where(x => x > 0);
```

Write method parameters as `IEnumerable<T>` when you only need to iterate; use `IList<T>` when you need indexed access.

## Collection comparison cheat sheet

| Type                         | Ordered | Unique | Key lookup | Notes                          |
|------------------------------|---------|--------|------------|--------------------------------|
| `T[]`                        | Yes     | No     | O(1) index | Fixed size                     |
| `List<T>`                    | Yes     | No     | O(1) index | Dynamic size                   |
| `Dictionary<TK, TV>`         | No      | Keys   | O(1)       | Key-value pairs                |
| `HashSet<T>`                 | No      | Yes    | O(1)       | Set operations (Union, Intersect) |
| `SortedDictionary<TK, TV>`   | Yes (key) | Keys | O(log n)  | Red-black tree                 |
| `Queue<T>`                   | Yes (FIFO) | No  | —          | Producer-consumer              |
| `Stack<T>`                   | Yes (LIFO) | No  | —          | Undo stacks, DFS               |

## Spans and Memory (advanced peek)

`Span<T>` is a stack-allocated view over a contiguous buffer — zero-allocation slicing:

```csharp
int[] data = { 1, 2, 3, 4, 5 };
Span<int> slice = data.AsSpan(1, 3);  // [2, 3, 4]
```

Use it in hot paths where you'd otherwise create temporary arrays.

## Key takeaways

- Default to `List<T>` for sequences, `Dictionary` for lookups, `HashSet` for membership tests.
- Program to interfaces (`IEnumerable`, `IList`) at API boundaries.
- `TryGetValue` is always safer than the `Dictionary` indexer for read operations.
