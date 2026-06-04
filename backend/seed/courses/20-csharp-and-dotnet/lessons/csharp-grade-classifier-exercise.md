# Exercise: Grade Classifier

This exercise trains the `int.Parse` / `TryParse` pattern combined with conditional branching — two skills that appear constantly in real C# applications such as reading user input, processing form data, and validating API payloads.

## What you will practice

- Parsing an integer from a string (`int.Parse` or `int.TryParse`)
- Chained `if / else if / else` branches for range checks
- Printing multiple lines of output from a single program

## The TryParse pattern

```csharp
string? raw = Console.ReadLine();

if (!int.TryParse(raw, out int score))
{
    Console.WriteLine("Invalid input");
    return;
}
```

`TryParse` returns `false` without throwing an exception when the input is not a valid integer. This is the preferred pattern for untrusted input (user forms, file reads, HTTP request parameters).

## Classifying grades

```csharp
string grade = score switch
{
    >= 90 => "A",
    >= 80 => "B",
    >= 70 => "C",
    >= 60 => "D",
    _     => "F",
};

Console.WriteLine(grade);
Console.WriteLine(grade == "F" ? "Fail" : "Pass");
```

The `switch` expression (C# 8+) is ideal here: each arm tests a condition, returns a value, and has no fall-through. The `>=` relational pattern is evaluated top-to-bottom, so writing the highest threshold first works cleanly.

## Common mistake to avoid

A frequent beginner error is checking `score >= 60` before `score >= 90`, which assigns "D" to every score from 60 upward because the first matching arm wins. Always write ranges from highest to lowest.

## Further reading

- *C# Programming Yellow Book* by Rob Miles — free PDF covering input/output and conditional logic — https://www.robmiles.com/c-yellow-book
- *Fundamentals of Computer Programming with C#* by Svetlin Nakov — Chapter 5 "Conditional Statements" — https://introprogramming.info/english-intro-csharp-book/downloads/
