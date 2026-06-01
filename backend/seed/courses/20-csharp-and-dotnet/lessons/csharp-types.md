# Types, Nullable, var

## Primitive types

```csharp
int        i = 42;
long       l = 1_000_000_000L;
double     d = 3.14;
decimal    m = 3.14m;        // 128-bit exact decimal, use for money
bool       b = true;
char       c = 'A';
string     s = "hello";
```

`decimal` is exact (`3.14m + 0.1m == 3.24m`). `double` is IEEE-754 with rounding errors. Use `decimal` for money.

## var

```csharp
var n = 5;                  // int
var name = "Alice";         // string
var users = new List<User>();
```

Type-inferred local variables. Required to be initialized at declaration. Use freely when the type is obvious from the right-hand side.

## Nullable reference types

When `<Nullable>enable</Nullable>` is on (the default for new projects), reference types are non-nullable by default:

```csharp
string  name = null;     // warning: cannot be null
string? maybe = null;    // OK, marked nullable
```

The compiler tracks possible-null flow:

```csharp
string? raw = TryGet();
// raw.Length;       // warning - possibly null
if (raw is not null) {
    raw.Length;      // OK
}
```

## Nullable value types

```csharp
int? age = null;
if (age.HasValue) { ... }
int defaulted = age ?? 0;
```

`int?` is shorthand for `Nullable<int>`. It's a value type that holds an `int` or `null`.

## String interpolation and verbatim

```csharp
string greeting = $"Hello, {name}, you are {age} years old.";
string multiline = $@"line 1
line 2 {name}";
string raw = """
    line 1
    line 2 with no escapes
    """;
```

The `"""..."""` raw string literal (C# 11+) is the cleanest for multi-line strings, JSON, regex, SQL.

## Operators worth noting

```csharp
a ?? b              // a if not null, else b
a?.b                // null-safe property access
a?[i]               // null-safe indexing
a is int n         // pattern matching + variable bind
a is { Length: > 0 }  // property pattern
```

```csharp
if (input is { Length: > 0 } s) { Console.WriteLine(s); }
```

## Collections (built-in)

```csharp
var nums = new List<int> { 1, 2, 3 };
var arr  = new[] { 1, 2, 3 };
var map  = new Dictionary<string, int> { ["a"] = 1, ["b"] = 2 };
var set  = new HashSet<string> { "x", "y" };
```

## Tuples

```csharp
var t = (Name: "Alice", Age: 30);
Console.WriteLine(t.Name);
(string n, int a) = t;            // deconstruct
```

Lightweight inline records. For named, reusable data shapes use `record` instead.

## Constants and readonly

```csharp
public const int MAX = 100;            // compile-time constant
public readonly int max;               // assignable only in ctor
```

For modules / static config use `const`. For instance state that can't change after construction use `readonly`.

## DateTime, Guid

```csharp
DateTime now = DateTime.UtcNow;        // always prefer UTC
Guid id = Guid.NewGuid();
TimeSpan d = TimeSpan.FromMinutes(5);
```

For modern code, prefer `DateTimeOffset` (or NodaTime's types) over `DateTime` to avoid time-zone bugs.
