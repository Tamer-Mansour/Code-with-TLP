# Streams and Lambdas

Java 8 added **lambdas** (anonymous functions) and the **Streams API** for functional-style data pipelines.

## Lambdas

```java
Runnable r = () -> System.out.println("hi");
Comparator<String> cmp = (a, b) -> a.length() - b.length();
Function<Integer, Integer> sq = n -> n * n;
BiFunction<Integer, Integer, Integer> add = (a, b) -> a + b;
```

A lambda is shorthand for an instance of a **functional interface** — an interface with one abstract method (`@FunctionalInterface`).

### Common functional interfaces

| Interface                | Shape                |
|--------------------------|----------------------|
| `Runnable`               | `void run()`         |
| `Supplier<T>`            | `T get()`            |
| `Consumer<T>`            | `void accept(T)`     |
| `Function<T, R>`         | `R apply(T)`         |
| `BiFunction<T, U, R>`    | `R apply(T, U)`      |
| `Predicate<T>`           | `boolean test(T)`    |
| `UnaryOperator<T>`       | `T apply(T)`         |

## Method references

```java
list.forEach(System.out::println);          // x -> System.out.println(x)
users.stream().map(User::name);             // u -> u.name()
new ArrayList<String>()::add;               // instance method
String::valueOf;                            // static method
```

## Streams — the pipeline

```java
import java.util.stream.*;

int total = users.stream()
    .filter(u -> u.isActive())
    .mapToInt(User::age)
    .sum();
```

Streams have:

- A **source** — `collection.stream()`, `Stream.of(...)`, `Files.lines(path)`.
- Zero or more **intermediate operations** — `filter`, `map`, `flatMap`, `sorted`, `distinct`, `limit`, `skip`, `peek`.
- One **terminal operation** — `collect`, `count`, `findFirst`, `reduce`, `forEach`, `toList`.

Streams are **lazy** — intermediate operations don't run until the terminal operation kicks them off.

## Collecting

```java
import static java.util.stream.Collectors.*;

List<String> names = users.stream().map(User::name).toList();   // 16+
List<String> names2 = users.stream().map(User::name).collect(toList());

Map<String, List<User>> byCountry = users.stream()
    .collect(groupingBy(User::country));

Map<String, Long> counts = users.stream()
    .collect(groupingBy(User::country, counting()));

String joined = users.stream()
    .map(User::name)
    .collect(joining(", ", "[", "]"));
```

## reduce

```java
int sum = nums.stream().reduce(0, Integer::sum);
int product = nums.stream().reduce(1, (a, b) -> a * b);
Optional<Integer> max = nums.stream().reduce(Integer::max);
```

## Primitive streams

For performance with primitives:

```java
IntStream.range(0, 10).sum();
nums.stream().mapToInt(Integer::intValue).average();
```

## Parallel streams

```java
users.parallelStream().filter(...).count();
```

Splits the work across the common ForkJoinPool. Use when:
- The pipeline is CPU-bound and substantial.
- Operations are stateless and side-effect-free.
- Source is splittable (arrays and `ArrayList` are; `LinkedList` isn't).

Skip when:
- You're doing I/O.
- The dataset is small.
- The operations have side effects or shared state.

`parallelStream` is easy to misuse — measure, don't guess.

## A real-world example

```java
Map<String, Double> avgAgePerCountry = users.stream()
    .filter(User::isActive)
    .collect(groupingBy(User::country, averagingInt(User::age)));
```

Readable, type-safe, parallelizable with one method change.
