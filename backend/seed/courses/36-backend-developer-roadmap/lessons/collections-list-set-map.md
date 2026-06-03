# Collections: List, Set, and Map

The Java Collections Framework (JCF) provides ready-made data structures that every backend developer uses daily. Three interfaces dominate day-to-day work: `List`, `Set`, and `Map`. Knowing which to reach for — and which concrete class to choose — is one of the most practical skills you can build.

## The Core Interfaces

| Interface | Allows duplicates | Ordered | Key-value pairs |
|-----------|:-----------------:|:-------:|:---------------:|
| `List`    | Yes               | Yes (insertion order) | No |
| `Set`     | No                | Depends on impl | No |
| `Map`     | Values yes, keys no | Depends on impl | Yes |

All three live in `java.util`. Import them (and their implementations) with:

```java
import java.util.*;
```

---

## List

A `List` is an ordered sequence where elements keep their insertion order and duplicates are permitted. The two implementations you will use most are:

- **`ArrayList`** — backed by a resizable array; O(1) random access, O(n) insert/delete in the middle.
- **`LinkedList`** — doubly-linked list; O(1) insert/delete at head or tail, O(n) random access.

```java
import java.util.ArrayList;
import java.util.List;

public class ListDemo {
    public static void main(String[] args) {
        List<String> languages = new ArrayList<>();
        languages.add("Java");
        languages.add("Python");
        languages.add("Go");
        languages.add("Java");          // duplicates are allowed

        System.out.println(languages);          // [Java, Python, Go, Java]
        System.out.println(languages.get(1));   // Python
        System.out.println(languages.size());   // 4

        languages.remove("Python");
        System.out.println(languages);          // [Java, Go, Java]

        // Iterate with an enhanced for-loop
        for (String lang : languages) {
            System.out.println(lang.toLowerCase());
        }
    }
}
```

**When to choose `ArrayList` vs `LinkedList`:**

Use `ArrayList` by default. Switch to `LinkedList` only when you are doing heavy insertion or removal at both ends of the list (e.g., implementing a queue manually). For pure random access or iteration `ArrayList` wins due to cache locality.

---

## Set

A `Set` guarantees uniqueness — adding an element that already exists is silently ignored. The three implementations worth knowing:

- **`HashSet`** — O(1) average add/remove/contains; no guaranteed iteration order.
- **`LinkedHashSet`** — same O(1) performance but preserves insertion order.
- **`TreeSet`** — O(log n) operations; always iterates in natural sorted order.

```java
import java.util.HashSet;
import java.util.LinkedHashSet;
import java.util.Set;
import java.util.TreeSet;

public class SetDemo {
    public static void main(String[] args) {
        Set<String> tags = new HashSet<>();
        tags.add("spring");
        tags.add("java");
        tags.add("spring");   // duplicate — ignored silently
        tags.add("rest");

        System.out.println(tags.size());          // 3 (not 4)
        System.out.println(tags.contains("java")); // true

        // TreeSet to get sorted output
        Set<Integer> scores = new TreeSet<>();
        scores.add(88);
        scores.add(72);
        scores.add(95);
        scores.add(72);       // duplicate — ignored
        System.out.println(scores); // [72, 88, 95]
    }
}
```

A common use case: deduplicate a list while preserving order.

```java
List<String> raw = List.of("a", "b", "a", "c", "b");
Set<String> unique = new LinkedHashSet<>(raw); // preserves order, removes dupes
System.out.println(unique); // [a, b, c]
```

---

## Map

A `Map` stores key-value pairs. Each key is unique; values may repeat. Main implementations:

- **`HashMap`** — O(1) average get/put; no guaranteed key order.
- **`LinkedHashMap`** — O(1) but iterates keys in insertion order.
- **`TreeMap`** — O(log n); iterates keys in natural sorted order.

```java
import java.util.HashMap;
import java.util.Map;

public class MapDemo {
    public static void main(String[] args) {
        Map<String, Integer> wordCount = new HashMap<>();

        String[] words = {"java", "spring", "java", "rest", "spring", "java"};
        for (String word : words) {
            wordCount.put(word, wordCount.getOrDefault(word, 0) + 1);
        }

        System.out.println(wordCount);          // {rest=1, spring=2, java=3}
        System.out.println(wordCount.get("java")); // 3
        System.out.println(wordCount.containsKey("go")); // false

        // Iterate over entries
        for (Map.Entry<String, Integer> entry : wordCount.entrySet()) {
            System.out.println(entry.getKey() + " -> " + entry.getValue());
        }
    }
}
```

`getOrDefault(key, defaultValue)` is the idiomatic Java way to safely read a map value without a `NullPointerException` when the key is absent.

---

## Common Mistakes and Best Practices

- **Program to the interface, not the implementation.** Declare variables as `List`, `Set`, or `Map`, not `ArrayList` or `HashMap`. This makes it easy to swap implementations later.

  ```java
  // Prefer this:
  List<String> items = new ArrayList<>();

  // Not this:
  ArrayList<String> items = new ArrayList<>();
  ```

- **Use `equals`/`hashCode` correctly in `HashSet` and `HashMap`.** If you store custom objects as keys or inside a `HashSet`, you must override both `equals` and `hashCode`. Java's `Objects.hash()` makes this straightforward.

- **Avoid raw types.** Always supply the generic type parameter (`List<String>`, not just `List`). Raw types lose compile-time type safety.

- **`Collections.unmodifiableList` vs `List.of`.** Use `List.of(...)`, `Set.of(...)`, and `Map.of(...)` (Java 9+) to create compact, truly immutable collections. These throw `UnsupportedOperationException` on any write attempt — ideal for returning constant data from methods.

  ```java
  List<String> colors = List.of("red", "green", "blue"); // immutable
  ```

- **`null` handling:** `HashMap` allows one `null` key and multiple `null` values. `TreeMap` does not allow `null` keys (it calls `compareTo`). `HashSet` allows one `null` element. Be explicit about whether `null` is a valid value in your domain.

---

## Choosing the Right Collection

| Scenario | Best choice |
|---|---|
| Ordered list, fast index access | `ArrayList` |
| Fast queue / deque operations | `LinkedList` or `ArrayDeque` |
| Eliminate duplicates, don't care about order | `HashSet` |
| Eliminate duplicates, preserve insertion order | `LinkedHashSet` |
| Sorted unique elements | `TreeSet` |
| Key-value lookup, fast and order-free | `HashMap` |
| Key-value lookup, insertion-ordered keys | `LinkedHashMap` |
| Key-value lookup, sorted keys | `TreeMap` |

---

`List`, `Set`, and `Map` cover the vast majority of data-organisation problems you will encounter in Java backend development — choose the right interface first, then pick the implementation that matches your ordering and performance requirements.
