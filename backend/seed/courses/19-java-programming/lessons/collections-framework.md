# Collections Framework

`java.util` ships generic collections. The headline interfaces:

- **`List<E>`** — ordered, allows duplicates. Impls: `ArrayList`, `LinkedList`.
- **`Set<E>`** — no duplicates. Impls: `HashSet`, `LinkedHashSet`, `TreeSet`.
- **`Queue<E>` / `Deque<E>`** — FIFO / both-ends. Impls: `ArrayDeque`, `LinkedList`.
- **`Map<K,V>`** — key→value. Impls: `HashMap`, `LinkedHashMap`, `TreeMap`, `ConcurrentHashMap`.

## Picking an impl

| Need                                | Use                  |
|-------------------------------------|----------------------|
| Index access, append-mostly         | `ArrayList`          |
| Insertions in the middle            | `LinkedList` (rare)  |
| Unique values, fast contains        | `HashSet`            |
| Unique + insertion order            | `LinkedHashSet`      |
| Unique + sorted                     | `TreeSet`            |
| Key lookup                          | `HashMap`            |
| Key lookup + insertion order        | `LinkedHashMap`      |
| Sorted by key                       | `TreeMap`            |
| Thread-safe map                     | `ConcurrentHashMap`  |
| Stack / double-ended queue          | `ArrayDeque`         |

## Creating collections

```java
List<Integer> a = new ArrayList<>();
a.add(1); a.add(2);

List<Integer> b = List.of(1, 2, 3);          // immutable
Map<String, Integer> m = Map.of("a", 1, "b", 2);
Set<String> s = Set.of("x", "y");
```

`List.of`, `Map.of`, `Set.of` create **immutable** collections — throws on `add`/`put`. For mutable, use `new ArrayList<>(List.of(...))`.

## Common operations

```java
list.size();
list.get(0);
list.add(99);
list.remove(0);
list.contains(42);
list.indexOf(42);

map.put("k", 1);
map.get("k");
map.getOrDefault("missing", 0);
map.containsKey("k");
map.computeIfAbsent("k", key -> compute(key));

set.add("x");
set.remove("x");
set.contains("x");
```

`computeIfAbsent` is a workhorse — find or create in one atomic call.

## Iteration

```java
for (var x : list) { ... }
list.forEach(System.out::println);

for (var entry : map.entrySet()) {
    String k = entry.getKey();
    Integer v = entry.getValue();
}

map.forEach((k, v) -> System.out.println(k + "=" + v));
```

## Sorting

```java
List<User> users = ...;
users.sort(Comparator.comparingLong(User::id));
users.sort(Comparator.comparing(User::name).thenComparing(User::id));
users.sort(Comparator.comparingInt(User::age).reversed());
```

For natural ordering on values that implement `Comparable`:

```java
users.sort(Comparator.naturalOrder());
```

## Converting to / from arrays

```java
String[] arr = list.toArray(new String[0]);
List<String> back = Arrays.asList(arr);          // fixed-size, backed by arr
List<String> mutable = new ArrayList<>(back);
```

## Useful utilities

```java
Collections.unmodifiableList(list);
Collections.emptyList();
Collections.reverse(list);
Collections.shuffle(list);
Collections.frequency(list, value);
```

## Thread safety

Most `java.util` collections are NOT thread-safe. For concurrent access:

- `ConcurrentHashMap` instead of `HashMap`.
- `CopyOnWriteArrayList` for read-heavy lists.
- `Collections.synchronizedXxx(...)` as a last resort (coarse-grained locking).

Wrong choice = silent corruption. Pick concurrent impls when sharing across threads.
