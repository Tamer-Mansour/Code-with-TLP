# Quiz: Collections, Generics, and Streams

**Q1. Which `List` implementation provides O(1) indexed access and O(n) insertions in the middle?**
- [x] `ArrayList`
- [ ] `LinkedList`
- [ ] `TreeList`
- [ ] `ArrayDeque`

**Q2. What does `Map.getOrDefault(key, fallback)` return when the key is absent?**
- [ ] `null`
- [ ] An empty `Optional`
- [x] The `fallback` value
- [ ] It throws `NoSuchElementException`

**Q3. A generic method signature `<T extends Comparable<T>> T max(T a, T b)` means:**
- [ ] `T` must be a primitive type.
- [x] `T` must implement `Comparable<T>`, allowing comparison with `compareTo`.
- [ ] `T` is always inferred as `Object`.
- [ ] `T` can be any interface.

**Q4. What is the difference between `Collection.stream()` and `Collection.parallelStream()`?**
- [ ] `parallelStream()` always produces results faster.
- [ ] `stream()` is lazy; `parallelStream()` is eager.
- [x] `parallelStream()` splits the work across multiple threads using the fork/join pool; `stream()` is single-threaded.
- [ ] They are identical; the choice only matters for debugging.

**Q5. Which terminal operation collects stream elements into a `List`?**
- [ ] `stream.toList()` is not valid.
- [ ] `stream.map(List::of)`
- [x] `stream.collect(Collectors.toList())` or `stream.toList()` (Java 16+)
- [ ] `stream.forEach(list::add)`

**Q6. A wildcard `List<? extends Number>` means:**
- [ ] The list elements can be written as any `Number` subtype.
- [x] The list is read-only for elements: you can read `Number` objects but cannot add elements (except `null`).
- [ ] It is equivalent to `List<Number>`.
- [ ] Only `Integer` elements are allowed.

**Q7. `HashMap` vs `TreeMap` — which statement is correct?**
- [ ] `HashMap` keeps keys in insertion order; `TreeMap` has O(log n) operations.
- [x] `HashMap` provides O(1) average-case operations; `TreeMap` keeps keys sorted and provides O(log n) operations.
- [ ] Both maintain natural ordering of keys.
- [ ] `TreeMap` is faster for all operations because of tree-based indexing.

**Q8. Which stream operation is a short-circuit terminal operation?**
- [ ] `forEach`
- [ ] `reduce`
- [x] `findFirst`
- [ ] `collect`
