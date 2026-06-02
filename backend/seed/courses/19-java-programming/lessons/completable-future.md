# CompletableFuture and Async Programming

`CompletableFuture<T>` (Java 8+) is Java's promise-like API for composing asynchronous computations without blocking threads.

## Creating a future

```java
import java.util.concurrent.*;

// Run in ForkJoinPool.commonPool()
CompletableFuture<String> f = CompletableFuture.supplyAsync(() -> {
    // simulate slow DB call
    Thread.sleep(500);
    return "Hello from async";
});

// Run in a custom executor
ExecutorService pool = Executors.newFixedThreadPool(4);
CompletableFuture<Integer> g = CompletableFuture.supplyAsync(() -> 42, pool);
```

## Transforming results

```java
CompletableFuture<Integer> length = f
    .thenApply(String::length);          // map: T -> U, still async

length.thenAccept(n -> System.out.println("Length: " + n)); // terminal consumer
```

## Chaining (flatMap equivalent)

```java
CompletableFuture<String> result = fetchUserId()
    .thenCompose(id -> fetchUserById(id))   // id -> CompletableFuture<User>
    .thenApply(user -> user.name());
```

`thenCompose` is the async equivalent of `flatMap` — it prevents nesting `CompletableFuture<CompletableFuture<T>>`.

## Combining two futures

```java
CompletableFuture<String> a = fetchWeather();
CompletableFuture<String> b = fetchNews();

// Wait for both, then combine
CompletableFuture<String> combined = a.thenCombine(b,
    (weather, news) -> weather + " | " + news);
```

## Waiting for all / any

```java
// All must complete
CompletableFuture<Void> all = CompletableFuture.allOf(f1, f2, f3);
all.join();  // blocks until all done

// First to finish wins
CompletableFuture<Object> any = CompletableFuture.anyOf(f1, f2, f3);
```

## Error handling

```java
CompletableFuture<String> safe = fetchData()
    .exceptionally(ex -> {
        System.err.println("Error: " + ex.getMessage());
        return "default";          // fallback value
    })
    .handle((value, ex) -> {       // always runs
        if (ex != null) return "fallback";
        return value.toUpperCase();
    });
```

## Blocking to get the result

```java
// Blocks (use only at the boundary, e.g., test or main thread)
String val = f.get();              // throws checked exceptions
String val2 = f.join();            // throws unchecked CompletionException
String val3 = f.getNow("default"); // returns default if not done yet
```

## Practical pipeline example

```java
// Fetch product data asynchronously, enrich it, then store it
CompletableFuture.supplyAsync(() -> productRepo.findById(42), dbPool)
    .thenApplyAsync(product -> enrichWithInventory(product), httpPool)
    .thenAcceptAsync(enriched -> cache.put(enriched.id(), enriched), cachePool)
    .exceptionally(ex -> { log.error("Pipeline failed", ex); return null; });
```

## Key method reference

| Method | Purpose |
|--------|---------|
| `supplyAsync(Supplier, [Executor])` | Start async computation |
| `thenApply(Function)` | Transform result (sync step) |
| `thenApplyAsync(Function, [Executor])` | Transform on different thread |
| `thenCompose(Function)` | Chain another future (flatMap) |
| `thenCombine(other, BiFunction)` | Combine two futures |
| `allOf(futures...)` | Wait for all |
| `anyOf(futures...)` | Wait for first |
| `exceptionally(Function)` | Handle error, return fallback |
| `handle(BiFunction)` | Always-runs handler (value or error) |
| `join()` | Block and get result (unchecked) |
| `get()` | Block and get result (checked) |

## Pitfalls

- Do not call `.get()` inside another async stage — it blocks a pool thread.
- Use a **separate executor** for blocking I/O stages to avoid starving the common pool.
- Return `CompletableFuture<Void>` from fire-and-forget chains; track errors via `exceptionally`.
