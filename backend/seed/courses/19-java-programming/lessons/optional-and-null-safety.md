# Optional and Null Safety

`NullPointerException` is called the "billion-dollar mistake." Java's `Optional<T>` (Java 8+) makes the absence of a value explicit in the type system instead of silently returning `null`.

## Creating an Optional

```java
import java.util.Optional;

Optional<String> present = Optional.of("hello");          // must be non-null
Optional<String> empty   = Optional.empty();
Optional<String> maybe   = Optional.ofNullable(null);     // safe — creates empty
Optional<String> maybe2  = Optional.ofNullable("world");  // creates non-empty
```

## Checking and getting the value

```java
Optional<String> opt = Optional.of("Java");

opt.isPresent();          // true
opt.isEmpty();            // false (Java 11)
opt.get();                // "Java" — throws NoSuchElementException if empty!
opt.orElse("default");    // "Java"

Optional<String> empty = Optional.empty();
empty.orElse("fallback");                         // "fallback"
empty.orElseGet(() -> computeDefault());          // lazy alternative
empty.orElseThrow(() -> new RuntimeException()); // throw if absent
```

**Avoid `opt.get()` without checking `isPresent()` first.** Prefer `orElse` / `orElseGet`.

## Transforming with map and flatMap

```java
Optional<String> upper = opt.map(String::toUpperCase); // Optional<String>
Optional<Integer> length = opt.map(String::length);     // Optional<Integer>

// flatMap: when the mapping function itself returns an Optional
Optional<String> username = findUser(id)
    .flatMap(user -> Optional.ofNullable(user.getUsername()));
```

## filter

```java
Optional<String> long_ = opt.filter(s -> s.length() > 3); // present
Optional<String> gone  = opt.filter(s -> s.length() > 10); // empty
```

## ifPresent and ifPresentOrElse

```java
opt.ifPresent(s -> System.out.println("Found: " + s));

opt.ifPresentOrElse(
    s -> System.out.println("Found: " + s),
    ()  -> System.out.println("Not found")     // Java 9+
);
```

## or (Java 9)

Chain fallback Optionals:

```java
Optional<String> result = findInCache(key)
    .or(() -> findInDatabase(key))
    .or(() -> Optional.of("default"));
```

## stream (Java 9)

Convert Optional to a zero-or-one-element Stream for use in pipelines:

```java
List<String> results = ids.stream()
    .map(repo::findById)          // returns Optional<User>
    .flatMap(Optional::stream)    // keep only present ones
    .map(User::name)
    .toList();
```

## When to use Optional

| Good use | Avoid |
|----------|-------|
| Return type of a method that might not find a value | Method parameter (use `@Nullable` and overloads instead) |
| Chaining transformations on a maybe-value | Instance field (adds boxing overhead) |
| Stream pipelines to filter absent values | Collections (`Optional<List<T>>` → return empty list instead) |

## Optional vs null — comparison

```java
// Null-style (fragile)
String name = user.getName(); // might be null
if (name != null) {
    System.out.println(name.toUpperCase());
}

// Optional-style (explicit)
user.getName()
    .map(String::toUpperCase)
    .ifPresent(System.out::println);
```

## Java 14+ records and null safety

Records make `null`-safe value types easier:

```java
record Point(double x, double y) {}

// Records are final, auto-implement equals/hashCode/toString
// Fields are final — once constructed, no mutation
var p = new Point(1.0, 2.0);
```

For nullable record fields, annotate with `@Nullable` (JSR-305 or Jakarta Annotation) to communicate intent to tooling.
