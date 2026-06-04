# Exception Handling and the IDisposable Pattern

Exceptions are the standard mechanism in C# for signalling and recovering from runtime errors. Writing code that handles exceptions gracefully — and cleans up resources reliably — is a core production skill.

## try / catch / finally

```csharp
try
{
    int result = int.Parse(Console.ReadLine()!);
    Console.WriteLine($"Parsed: {result}");
}
catch (FormatException ex)
{
    Console.WriteLine($"Bad format: {ex.Message}");
}
catch (OverflowException)
{
    Console.WriteLine("Number too large for int.");
}
finally
{
    Console.WriteLine("This always runs.");
}
```

- `catch` blocks are tested in order — most specific first.
- `finally` always executes, whether an exception was thrown or not. Use it to release resources.

## The Exception hierarchy

```
System.Exception
├── System.SystemException
│   ├── ArgumentNullException
│   ├── ArgumentOutOfRangeException
│   ├── InvalidOperationException
│   ├── NullReferenceException
│   ├── FormatException
│   └── OverflowException
└── System.ApplicationException  (convention: your custom exceptions)
```

Catch the **most specific type** you can handle. Catching `Exception` is a last-resort base case.

## Throwing exceptions

```csharp
// Preserve the original stack trace
catch (IOException ex)
{
    _logger.LogError(ex, "File read failed");
    throw;                // re-throw with original stack trace
}

// DON'T do this — loses the original stack trace
catch (IOException ex)
{
    throw ex;             // stack trace reset to this line
}
```

Always use bare `throw;` to rethrow. `throw ex;` is almost always wrong.

## Custom exception classes

```csharp
public class ValidationException : Exception
{
    public string FieldName { get; }

    public ValidationException(string fieldName, string message)
        : base(message)
    {
        FieldName = fieldName;
    }

    public ValidationException(string fieldName, string message, Exception inner)
        : base(message, inner)
    {
        FieldName = fieldName;
    }
}
```

Always provide the two constructors shown — one without and one with an `inner` exception. The inner exception pattern lets callers inspect the original cause.

## IDisposable and the using statement

```csharp
// Classic using statement — calls Dispose() automatically
using (var reader = new StreamReader("data.txt"))
{
    string? line;
    while ((line = reader.ReadLine()) != null)
        Console.WriteLine(line);
}

// Shorter using declaration (C# 8+)
using var reader = new StreamReader("data.txt");
// Dispose is called when reader goes out of scope
```

Any class that holds unmanaged resources (file handles, database connections, network sockets) should implement `IDisposable`. Always wrap such objects in a `using` block to guarantee cleanup even if an exception is thrown.

## Defensive coding: TryParse over parse

```csharp
// Throws FormatException on invalid input
int n = int.Parse(userInput);

// Safe — returns false instead of throwing
if (!int.TryParse(userInput, out int n))
{
    Console.WriteLine("Please enter a valid integer.");
    return;
}
```

Prefer `TryParse` for any input you do not fully control.

## Key corrections

A common misconception: the garbage collector does **not** call `Dispose`. The GC frees memory; `IDisposable.Dispose` frees other resources (file handles, connections). The GC is also non-deterministic — an unreferenced object may stay in memory until the GC decides to collect it. Never rely on the GC for timely cleanup of unmanaged resources.

## Further reading

- *C# Notes for Professionals* — "Exception Handling" chapter — https://books.goalkicker.com/CSharpBook/
- *Fundamentals of Computer Programming with C#* — Chapter 12 "Exception Handling" — https://introprogramming.info/english-intro-csharp-book/downloads/
