# Strings in C#

`string` in C# is an alias for `System.String` — an immutable, Unicode (UTF-16) sequence of characters. Immutability means every "modification" returns a new string; the original is unchanged.

## Creating strings

```csharp
string greeting = "Hello, World!";
string name     = "Alice";

// Interpolation ($"...") — preferred
string msg = $"Hello, {name}. You have {42} messages.";

// Verbatim (@"...") — raw string, no escape needed
string path = @"C:\Users\Alice\Documents";

// Raw string literals (C# 11+) — triple-quote, great for JSON/SQL
string json = """
    {
        "key": "value"
    }
    """;
```

## Common string operations

```csharp
string s = "  Hello, World!  ";

Console.WriteLine(s.Trim());               // "Hello, World!"
Console.WriteLine(s.ToUpper());            // "  HELLO, WORLD!  "
Console.WriteLine(s.Replace("World", "C#")); // "  Hello, C#!  "
Console.WriteLine(s.Contains("World"));    // True
Console.WriteLine(s.StartsWith("  H"));   // True
Console.WriteLine(s.IndexOf("World"));    // 9 (after trimming offset)

// Split and Join
string csv = "a,b,c,d";
string[] parts = csv.Split(',');           // ["a","b","c","d"]
string joined = string.Join(" | ", parts); // "a | b | c | d"

// Substring
string sub = "Hello World".Substring(6, 5);  // "World"
// or with range operator (C# 8+)
string sub2 = "Hello World"[6..];            // "World"
```

## String comparison

```csharp
// NEVER use == for culture-aware comparison in production
string a = "Café";
string b = "cafe";

bool eq = string.Equals(a, b, StringComparison.OrdinalIgnoreCase); // true

// Sorting with culture
var words = new[] { "banana", "apple", "cherry" };
Array.Sort(words, StringComparer.OrdinalIgnoreCase);
```

| Comparison type               | Use when                                    |
|-------------------------------|---------------------------------------------|
| `Ordinal`                     | File paths, identifiers, hash keys          |
| `OrdinalIgnoreCase`           | Case-insensitive IDs, config keys           |
| `CurrentCulture`              | Display text sorted for the user's locale   |
| `InvariantCulture`            | Serialized data, cross-machine consistency  |

## StringBuilder — mutable accumulator

Concatenating strings in a loop creates O(n²) garbage. Use `StringBuilder`:

```csharp
using System.Text;

var sb = new StringBuilder();
for (int i = 0; i < 1000; i++)
    sb.Append(i).Append(',');

sb.Length--;                   // trim last comma
string result = sb.ToString();
```

Rule of thumb: use `StringBuilder` when you concatenate in a loop or append more than ~5 times.

## Parsing and formatting numbers

```csharp
int n    = int.Parse("42");
double d = double.Parse("3.14");

// Safe parsing — no exception on bad input
if (int.TryParse(userInput, out int value))
    Console.WriteLine($"Parsed: {value}");

// Formatting
Console.WriteLine(1234567.89.ToString("N2"));  // "1,234,567.89"
Console.WriteLine(0.45.ToString("P1"));         // "45.0 %"
Console.WriteLine(255.ToString("X2"));          // "FF"
```

## Span\<char\> and allocation-free slicing

For high-throughput code (parsers, serializers), avoid creating substring allocations:

```csharp
ReadOnlySpan<char> span = "Hello, World!".AsSpan();
ReadOnlySpan<char> hello = span[..5];   // no allocation
Console.WriteLine(hello.ToString());    // "Hello"
```

## Key takeaways

- Strings are immutable — build them with interpolation or `StringBuilder`.
- Always specify a `StringComparison` mode when comparing for equality or sorting.
- Use verbatim (`@`) or raw (`"""`) literals for paths, regexes, and multi-line text.
- `TryParse` is safer than `Parse` for user-supplied input.
