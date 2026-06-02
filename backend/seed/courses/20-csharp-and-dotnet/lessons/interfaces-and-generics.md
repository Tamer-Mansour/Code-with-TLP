# Interfaces and Generics

Interfaces and generics are the backbone of reusable, type-safe C# code. Mastering them lets you write libraries that work on any type while still catching errors at compile time.

## Interfaces

An interface declares a contract — a set of members that implementing types must provide. Since C# 8, interfaces may also have default implementations.

```csharp
public interface IAnimal
{
    string Name { get; }
    void Speak();
}

public class Dog : IAnimal
{
    public string Name { get; }
    public Dog(string name) => Name = name;
    public void Speak() => Console.WriteLine($"{Name} says: Woof!");
}

public class Cat : IAnimal
{
    public string Name { get; }
    public Cat(string name) => Name = name;
    public void Speak() => Console.WriteLine($"{Name} says: Meow!");
}

// Polymorphism via interface
IAnimal[] animals = { new Dog("Rex"), new Cat("Whiskers") };
foreach (var a in animals)
    a.Speak();
```

A class can implement multiple interfaces (C# has no multiple class inheritance):

```csharp
public interface ISerializable { string Serialize(); }
public interface ICloneable<T>  { T Clone(); }

public class Config : ISerializable, ICloneable<Config>
{
    public string Serialize() => "...";
    public Config Clone()     => new Config();
}
```

## Generics

Generics let you write a single type or method that works for many concrete types, with full type safety and no boxing overhead for value types.

### Generic class

```csharp
public class Stack<T>
{
    private readonly List<T> _items = new();

    public void Push(T item)   => _items.Add(item);
    public T    Pop()          { var t = _items[^1]; _items.RemoveAt(_items.Count - 1); return t; }
    public int  Count          => _items.Count;
}

var intStack    = new Stack<int>();
var stringStack = new Stack<string>();
intStack.Push(1);
intStack.Push(2);
Console.WriteLine(intStack.Pop()); // 2
```

### Generic method

```csharp
public static T Max<T>(T a, T b) where T : IComparable<T>
    => a.CompareTo(b) >= 0 ? a : b;

Console.WriteLine(Max(3, 7));         // 7
Console.WriteLine(Max("apple", "banana")); // banana
```

### Constraints

| Constraint              | Meaning                                       |
|-------------------------|-----------------------------------------------|
| `where T : class`       | T must be a reference type                    |
| `where T : struct`      | T must be a value type                        |
| `where T : new()`       | T must have a parameterless constructor       |
| `where T : SomeBase`    | T must inherit from `SomeBase`                |
| `where T : IFoo`        | T must implement interface `IFoo`             |
| `where T : IComparable<T>` | T supports ordering                        |

## Covariance and contravariance

Generic interfaces can be covariant (`out T` — producer) or contravariant (`in T` — consumer):

```csharp
// IEnumerable<out T> is covariant
IEnumerable<Dog>    dogs  = new List<Dog>();
IEnumerable<IAnimal> animals = dogs;   // OK — Dog is an IAnimal

// IComparer<in T> is contravariant
IComparer<IAnimal> byName = Comparer<IAnimal>.Create((a, b) => string.Compare(a.Name, b.Name));
IComparer<Dog> dogByName = byName;    // OK
```

## A real-world example — generic repository

```csharp
public interface IRepository<T> where T : class
{
    T?          GetById(int id);
    IList<T>    GetAll();
    void        Add(T entity);
    void        Delete(int id);
}

public class InMemoryRepository<T> : IRepository<T> where T : class
{
    private readonly Dictionary<int, T> _store = new();
    private int _nextId = 1;

    public T? GetById(int id) => _store.GetValueOrDefault(id);
    public IList<T> GetAll()  => _store.Values.ToList();
    public void Add(T entity) => _store[_nextId++] = entity;
    public void Delete(int id)=> _store.Remove(id);
}
```

## Key takeaways

- Interfaces define contracts; classes and structs implement them. A class can implement many interfaces.
- Generics let you write type-safe, reusable code without sacrificing performance.
- Constraints (`where T : ...`) unlock operations on the type parameter.
- Prefer generic types over `object` or casting — errors surface at compile time, not runtime.
