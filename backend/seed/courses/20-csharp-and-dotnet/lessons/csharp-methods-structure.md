# Methods and Program Structure

Methods are the primary unit of code reuse in C#. Understanding parameters, return types, and overloading lets you write clean, maintainable programs from your very first project.

## Defining and calling a static method

```csharp
static int Add(int a, int b)
{
    return a + b;
}

// Expression-bodied shorthand (C# 6+)
static int Multiply(int a, int b) => a * b;

int sum = Add(3, 4);     // 7
```

`static` methods belong to the class, not to an instance. In top-level programs (C# 9+) all local functions are implicitly static unless they capture variables.

## Parameters: value, ref, and out

```csharp
// Value — a copy is passed; original is unchanged
static void DoubleIt(int n) { n *= 2; }

// ref — caller and method share the same variable
static void DoubleRef(ref int n) { n *= 2; }
int x = 5;
DoubleRef(ref x);   // x is now 10

// out — method must assign the variable before returning
static bool TryDivide(int a, int b, out int result)
{
    if (b == 0) { result = 0; return false; }
    result = a / b;
    return true;
}

if (TryDivide(10, 2, out int quotient))
    Console.WriteLine(quotient);   // 5
```

The `out` pattern is the standard C# idiom for "try to compute a value, return whether it succeeded."

## params — variable argument lists

```csharp
static int Sum(params int[] numbers)
{
    int total = 0;
    foreach (int n in numbers) total += n;
    return total;
}

Sum(1, 2, 3);          // 6 — caller passes individual ints
Sum(new[] { 1, 2 });   // also valid
```

`params` must be the last parameter. It packages the trailing arguments into an array automatically.

## Method overloading

```csharp
static string Format(int value)      => value.ToString();
static string Format(double value)   => $"{value:F2}";
static string Format(string value)   => $"\"{value}\"";
```

The compiler picks the right overload based on the argument type at compile time. Overloads must differ in parameter count or types — not just return type.

## Optional parameters and named arguments

```csharp
static void Connect(string host, int port = 5432, bool ssl = true)
{
    Console.WriteLine($"Connecting to {host}:{port} ssl={ssl}");
}

Connect("localhost");                         // port=5432, ssl=true
Connect("db.prod.com", ssl: false);           // named arg skips port
Connect("staging.com", port: 3306, ssl: true);
```

Named arguments make call sites self-documenting and let you skip optional parameters in the middle.

## Recursion

```csharp
static int Factorial(int n)
{
    if (n <= 1) return 1;          // base case
    return n * Factorial(n - 1);   // recursive call
}
```

Every recursive function needs a **base case** that stops the recursion. Without one, you get a `StackOverflowException`. For deep recursion (thousands of levels) consider converting to an iterative loop instead.

## Local functions

```csharp
static double HypotenuseSq(double a, double b)
{
    return Square(a) + Square(b);

    double Square(double x) => x * x;   // local function — only visible inside HypotenuseSq
}
```

Local functions are ideal for helper logic that is only needed inside one method. They can capture variables from the enclosing scope.

## Further reading

- *Programming Basics with C# (SoftUni)* — Chapter 10 "Methods" — https://csharp-book.softuni.org/
- *C# Programming Yellow Book* by Rob Miles — Chapter 3 "Writing Programs" — https://www.robmiles.com/c-yellow-book
