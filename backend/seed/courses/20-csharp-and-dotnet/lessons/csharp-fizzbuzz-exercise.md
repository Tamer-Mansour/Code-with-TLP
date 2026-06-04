# Exercise: FizzBuzz .NET Style

FizzBuzz is the canonical first exercise in every C# beginner course. It tests your understanding of loops, conditional branches, and the modulo operator — all fundamentals you will use every day.

## What you will practice

- Reading an integer from standard input using `int.Parse` / `Console.ReadLine()`
- Writing a `for` loop from 1 to N
- Using `%` (modulo) to check divisibility
- Chaining `if / else if / else` blocks in the correct order

## The classic pattern

```csharp
int n = int.Parse(Console.ReadLine()!);

for (int i = 1; i <= n; i++)
{
    if (i % 15 == 0)
        Console.WriteLine("FizzBuzz");
    else if (i % 3 == 0)
        Console.WriteLine("Fizz");
    else if (i % 5 == 0)
        Console.WriteLine("Buzz");
    else
        Console.WriteLine(i);
}
```

Notice that the `% 15` check (divisible by both 3 and 5) must come **first** — otherwise `i % 3` or `i % 5` would match before you reach the combined case.

## Why check `% 15` first?

If you wrote `if (i % 3 == 0)` first, then `15` would always print `"Fizz"` and never reach the FizzBuzz branch. The combined case is more specific, so it belongs at the top of the chain.

## Further reading

- *Programming Basics with C# (SoftUni)* — Chapter 4 "More Complex Conditions" — https://csharp-book.softuni.org/
- *C# Programming Yellow Book* by Rob Miles — Chapter 2 covers loops and conditions with a similar warm-up exercise — https://www.robmiles.com/c-yellow-book
