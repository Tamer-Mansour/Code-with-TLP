# Collections and Generics in C#

C# ships a rich set of strongly-typed collection classes in `System.Collections.Generic`. Generics let you write code that works with any type while keeping full compile-time safety — no casting, no `ArrayList` surprises.

## Arrays

```csharp
int[] scores = new int[5];           // zero-initialized
int[] primes = { 2, 3, 5, 7, 11 };  // initializer syntax
string[,] grid = new string[3, 4];   // 2-D array
int[][] jagged = new int[3][];       // jagged (each row its own length)
jagged[0] = new int[] { 1, 2 };
jagged[1] = new int[] { 3, 4, 5 };
```

Use arrays when the length is fixed and performance is critical. For everything else, prefer `List<T>`.

## List\<T\>

```csharp
var names = new List<string>();
names.Add("Alice");
names.Add("Bob");
names.Insert(0, "Zara");    // insert at index
names.Remove("Bob");
names.Sort();

foreach (var name in names)
    Console.WriteLine(name);
```

`List<T>` is a resizable array under the hood. Random access is O(1); insertion and removal in the middle are O(n).

## Dictionary\<TKey, TValue\>

```csharp
var wordCount = new Dictionary<string, int>();

foreach (var word in text.Split(' '))
{
    if (wordCount.ContainsKey(word))
        wordCount[word]++;
    else
        wordCount[word] = 1;
}

// Cleaner with TryGetValue:
wordCount.TryGetValue(word, out int count);
wordCount[word] = count + 1;

// Modern pattern — GetValueOrDefault:
wordCount[word] = wordCount.GetValueOrDefault(word, 0) + 1;
```

Dictionary lookup is O(1) average. Keys must be unique; duplicate keys throw `ArgumentException`.

## HashSet\<T\>

```csharp
var visited = new HashSet<string>();
visited.Add("page1");
visited.Add("page1");    // duplicate — silently ignored
bool seen = visited.Contains("page1");  // true
```

Use `HashSet<T>` when you only care about membership (not order or count). Contains, Add, Remove are all O(1) average.

## Queue\<T\> and Stack\<T\>

```csharp
// Queue — FIFO
var q = new Queue<string>();
q.Enqueue("first");
q.Enqueue("second");
string next = q.Dequeue();   // "first"

// Stack — LIFO
var s = new Stack<int>();
s.Push(1);
s.Push(2);
int top = s.Pop();           // 2
```

Classic data structure types — useful for BFS queues, undo stacks, and bracket-matching problems.

## Generic type parameters and constraints

```csharp
public T Max<T>(T a, T b) where T : IComparable<T>
{
    return a.CompareTo(b) >= 0 ? a : b;
}

int biggest = Max(3, 7);         // 7
string later = Max("apple", "cherry");  // "cherry"
```

The `where T : IComparable<T>` constraint tells the compiler that `T` supports comparison — otherwise `a.CompareTo(b)` would not compile.

Common constraints:

| Constraint | Meaning |
|------------|---------|
| `where T : class` | T must be a reference type |
| `where T : struct` | T must be a value type |
| `where T : new()` | T must have a parameterless constructor |
| `where T : ISomething` | T must implement the interface |

## Collection initializers and object initializers

```csharp
var map = new Dictionary<string, int>
{
    ["a"] = 1,
    ["b"] = 2,
    ["c"] = 3,
};

var users = new List<User>
{
    new() { Name = "Alice", Age = 30 },
    new() { Name = "Bob",   Age = 25 },
};
```

Clean syntax that avoids separate `Add` calls. Works with any type that implements `IEnumerable` and has an `Add` method.

## IEnumerable\<T\> — the universal interface

```csharp
void PrintAll<T>(IEnumerable<T> items)
{
    foreach (var item in items)
        Console.WriteLine(item);
}
```

`IEnumerable<T>` is the lowest-common-denominator interface. Accept it in method parameters when you only need to iterate — your method will work with arrays, lists, query results, and custom generators.

## Further reading

- *Fundamentals of Computer Programming with C#* — Chapters 19-21 on data structures — https://introprogramming.info/english-intro-csharp-book/downloads/
- *C# Notes for Professionals* — "Generic Collections" section — https://books.goalkicker.com/CSharpBook/
