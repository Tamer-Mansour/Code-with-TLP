# Control Flow in C#

C# provides the usual suspects for control flow — plus a few sharp additions like pattern-matching `switch` expressions and the null-coalescing operators that make conditional code dramatically shorter.

## if / else

```csharp
int score = 72;

if (score >= 90)
    Console.WriteLine("A");
else if (score >= 70)
    Console.WriteLine("B or C");
else
    Console.WriteLine("Below 70");
```

Use braces `{}` even for single-line bodies in team code — it prevents accidental bugs when adding lines later.

## switch statement

The classic form — useful when matching an integer or enum:

```csharp
var day = DayOfWeek.Monday;

switch (day)
{
    case DayOfWeek.Saturday:
    case DayOfWeek.Sunday:
        Console.WriteLine("Weekend");
        break;
    default:
        Console.WriteLine("Weekday");
        break;
}
```

## switch expression (C# 8+)

The modern, expression-oriented form — returns a value and has no fall-through:

```csharp
string label = day switch
{
    DayOfWeek.Saturday or DayOfWeek.Sunday => "Weekend",
    DayOfWeek.Monday                       => "Start of week",
    _                                      => "Mid-week",
};
```

`_` is the discard (wildcard). The `or` keyword chains patterns without repetition.

## Pattern matching

C# 9+ patterns let you match on type, value, and structure in one expression:

```csharp
object obj = 42;

string result = obj switch
{
    int n when n < 0  => "negative int",
    int n             => $"positive int {n}",
    string s          => $"string: {s}",
    null              => "null",
    _                 => "other",
};
```

You can also use `is` inline:

```csharp
if (obj is int n && n > 10)
    Console.WriteLine($"Big number: {n}");
```

## for / foreach / while

```csharp
// Classic for
for (int i = 0; i < 5; i++)
    Console.WriteLine(i);

// foreach — use for any IEnumerable
var fruits = new[] { "apple", "banana", "cherry" };
foreach (var fruit in fruits)
    Console.WriteLine(fruit);

// while
int x = 0;
while (x < 3)
{
    Console.WriteLine(x);
    x++;
}

// do-while — body executes at least once
do
{
    Console.Write("Enter a number: ");
} while (!int.TryParse(Console.ReadLine(), out int _));
```

## break, continue, and return

| Keyword    | Effect                                      |
|------------|---------------------------------------------|
| `break`    | Exit the innermost loop or switch           |
| `continue` | Skip to the next iteration                 |
| `return`   | Exit the method, optionally with a value    |

## Null-conditional and null-coalescing

These operators shrink verbose null checks:

```csharp
string? name = null;

int len  = name?.Length ?? 0;   // null-conditional + null-coalescing
string s = name ?? "default";   // just null-coalescing
name    ??= "fallback";         // assign only if null
```

`?.` short-circuits to `null` if the left side is null, avoiding `NullReferenceException`.

## Ternary operator

```csharp
int abs = x >= 0 ? x : -x;
```

Keep ternaries simple — nest them only when the result is immediately obvious.

## Key takeaways

- Prefer `switch` expressions over `switch` statements for value-producing logic.
- Pattern matching with `is` and `when` replaces many `if`/`else` chains.
- `?.` and `??` are your primary tools for safe null handling in C#.
