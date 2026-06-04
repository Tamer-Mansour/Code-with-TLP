# Exercise: Class Instance Counter

This exercise simulates a core OOP pattern taught in every .NET beginner course: a class that tracks how many instances of itself have been created using a **static counter field**.

## What you will practice

- Defining a class with instance fields and a constructor
- Using a `static` field shared across all instances
- Storing objects in a `List<T>` and iterating with `foreach`
- String interpolation for formatted output

## The Student class pattern

```csharp
public class Student
{
    public string Name { get; }
    public int Age { get; }
    private static int _count = 0;

    public Student(string name, int age)
    {
        Name = name;
        Age = age;
        _count++;
    }

    public static int Count => _count;
}
```

Every time `new Student(...)` is called, the constructor increments `_count`. Because `_count` is `static`, it belongs to the **class**, not to any single instance — all instances share the same counter.

## Reading input and populating the list

```csharp
int n = int.Parse(Console.ReadLine()!);
var students = new List<Student>();

for (int i = 0; i < n; i++)
{
    var parts = Console.ReadLine()!.Split(' ');
    students.Add(new Student(parts[0], int.Parse(parts[1])));
}

foreach (var s in students)
    Console.WriteLine($"Name: {s.Name}, Age: {s.Age}");

Console.WriteLine($"Total students: {Student.Count}");
```

## Key concept: static vs instance

| Member kind | Belongs to      | Shared?  |
|-------------|-----------------|----------|
| Instance field/property | One object | No — each object has its own copy |
| `static` field/property | The class itself | Yes — all objects share one copy |

This distinction is fundamental when implementing counters, caches, configuration singletons, and factory patterns in C#.

## Further reading

- *Fundamentals of Computer Programming with C#* — Chapter 14 "Defining Classes" — https://introprogramming.info/english-intro-csharp-book/downloads/
- *C# Notes for Professionals* — "Static Classes and Static Members" chapter — https://books.goalkicker.com/CSharpBook/
