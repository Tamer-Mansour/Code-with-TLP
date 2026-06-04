# Exercise: Inventory Filter with Streams

Modern Java encourages expressing data-transformation pipelines using the Streams API instead of manual loops. This exercise lets you practise the most common stream operations: `filter`, `map`, `sorted`, and `collect`.

## The Java stream pipeline

```java
List<Item> items = loadItems();

List<String> result = items.stream()
    .filter(item -> item.getPrice() <= maxPrice)
    .sorted(Comparator.comparingInt(Item::getPrice))
    .map(item -> item.getName() + " " + item.getPrice())
    .collect(Collectors.toList());

result.forEach(System.out::println);
```

Stream operations come in two flavours:
- **Intermediate** — `filter`, `map`, `sorted`, `distinct`, `limit` — lazy, return a new stream.
- **Terminal** — `collect`, `forEach`, `count`, `findFirst` — eager, trigger evaluation.

Nothing executes until a terminal operation is called. This allows the JVM to fuse operations and optimise the pipeline.

## Optional in pipeline design

When a result might not exist, `Optional` prevents `null` from propagating:

```java
Optional<Item> cheapest = items.stream()
    .filter(i -> i.getPrice() < 10)
    .min(Comparator.comparingInt(Item::getPrice));

cheapest.ifPresentOrElse(
    i -> System.out.println("Found: " + i.getName()),
    () -> System.out.println("None found")
);
```

## Problem statement

Read `N` on the first line, then `N` lines, each containing a product name and price separated by a space. Then read a budget integer `B` on the last line.

Print the names of all products with price **≤ B**, sorted by price ascending. If two products share the same price, sort alphabetically by name. If no products qualify, print `No items found`.

### Example

Input:
```
5
apple 2
banana 1
cherry 5
date 3
elderberry 1
B=3
```

Wait — let me simplify the format (no "B=" prefix):

Input:
```
5
apple 2
banana 1
cherry 5
date 3
elderberry 1
3
```

Output:
```
banana 1
elderberry 1
apple 2
date 3
```

## Further reading

- David J. Eck, *Introduction to Programming Using Java* (9th ed.) — Chapter 10: Generic Programming and Collection Classes: https://math.hws.edu/javanotes/
- *Think Java* (2nd ed.) — Chapter 14: Objects of Arrays: https://greenteapress.com/wp/think-java-2e/
