# Exercise: Dictionary Word Frequency

This exercise models the `Dictionary<string, int>` pattern — one of the most commonly used collection types in production C# code. You will count word occurrences and sort the output, mirroring what you would write with `GroupBy` and `OrderBy` in a real LINQ pipeline.

## What you will practice

- Reading a single line of space-separated tokens
- Building a `Dictionary<string, int>` frequency map
- Case-insensitive comparison using `.ToLower()` or `StringComparer.OrdinalIgnoreCase`
- Sorting by key with `OrderBy` (LINQ) or by converting to a sorted structure

## The Dictionary approach

```csharp
string line = Console.ReadLine()!;
string[] words = line.ToLower().Split(' ', StringSplitOptions.RemoveEmptyEntries);

var freq = new Dictionary<string, int>();
foreach (var word in words)
{
    freq.TryGetValue(word, out int count);
    freq[word] = count + 1;
}

foreach (var kv in freq.OrderBy(kv => kv.Key))
    Console.WriteLine($"{kv.Key}: {kv.Value}");
```

`OrderBy` is a LINQ extension method — it returns an `IOrderedEnumerable<T>` without modifying the original dictionary.

## The SortedDictionary shortcut

```csharp
var freq = new SortedDictionary<string, int>(StringComparer.Ordinal);
```

`SortedDictionary<TKey, TValue>` maintains keys in sorted order automatically. Insert and lookup are O(log n) instead of O(1), but for typical word-frequency problems this trade-off is irrelevant.

## Case sensitivity

Two common patterns:

```csharp
// Option 1 — normalise before inserting
string normalised = word.ToLower();

// Option 2 — case-insensitive dictionary
var freq = new Dictionary<string, int>(StringComparer.OrdinalIgnoreCase);
```

Option 2 is safer when you want to preserve the original casing in output. Option 1 (normalise first) is cleaner when lowercase output is acceptable — as in this exercise.

## Common mistake

Using `freq[word]++` without initialising the key first will throw a `KeyNotFoundException`. Always initialise with 0 first, or use `TryGetValue` / `GetValueOrDefault`.

## Further reading

- *C# Notes for Professionals* — "Dictionary" section — https://books.goalkicker.com/CSharpBook/
- *Fundamentals of Computer Programming with C#* — Chapter 18 "Dictionaries, Hash-Tables and Sets" — https://introprogramming.info/english-intro-csharp-book/downloads/
