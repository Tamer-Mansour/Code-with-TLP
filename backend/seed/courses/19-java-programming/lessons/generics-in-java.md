# Generics

Generics parameterize types with other types. The collections framework is the most-used example.

## Generic classes

```java
public class Box<T> {
    private T value;
    public Box(T value) { this.value = value; }
    public T get() { return value; }
    public <U> Box<U> map(Function<T, U> f) { return new Box<>(f.apply(value)); }
}

var b = new Box<>("hi").map(String::length);   // Box<Integer>
```

`<T>` is a type parameter. The diamond `<>` lets the compiler infer.

## Generic methods

```java
public static <T> T first(List<T> xs) {
    return xs.get(0);
}

first(List.of(1, 2));        // T = Integer
first(List.of("a"));         // T = String
```

## Bounded type parameters

```java
public static <T extends Number> double sum(List<T> xs) {
    double total = 0;
    for (T x : xs) total += x.doubleValue();
    return total;
}
```

`T extends Number` means "any subtype of Number" — Integer, Long, Double.

## Wildcards

```java
List<? extends Number> readNums;     // can read Numbers, can't add (PECS)
List<? super Integer> writeInts;     // can add Integers, reads as Object

void readAll(List<? extends Animal> animals) {
    for (Animal a : animals) a.speak();
}

void addDogs(List<? super Dog> sink) {
    sink.add(new Dog());
}
```

The mnemonic: **PECS — Producer Extends, Consumer Super.** Source you only read from? `? extends`. Sink you only write to? `? super`.

## Type erasure

The JVM doesn't know about generics at runtime. `List<String>` and `List<Integer>` are the same class. Consequences:

- `instanceof List<String>` won't compile (use `instanceof List<?>`).
- You can't `new T()` — no constructor for an erased type.
- Generic arrays are awkward: `T[] arr = new T[10];` doesn't work.

The compile-time guarantees still hold: you'd never see a `String` in a `List<Integer>`. The erasure just means you can't reflect on the type parameter at runtime.

## Recursive bounds — F-bounded

```java
public interface Comparable<T extends Comparable<T>> { ... }
```

Looks weird; means "T must be comparable with itself." It's how methods like `sort` work generically while keeping type safety.

## Generics + records

```java
public record Pair<A, B>(A first, B second) {}
var p = new Pair<>("Alice", 30);          // Pair<String, Integer>
```

## A practical interface example

```java
public interface Repository<T, ID> {
    Optional<T> findById(ID id);
    List<T> findAll();
    void save(T item);
}

public class UserRepo implements Repository<User, Long> { ... }
```

The compiler will hold the impl to exactly these signatures.

## When NOT to generic-ize

If your "generic" class only ever holds `String`, just use `String`. Generics are for reuse across many concrete types — not for showing off.
