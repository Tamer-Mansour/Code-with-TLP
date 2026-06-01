# Threads and ExecutorService

Java has had threads from day one. Modern Java code rarely creates `Thread` directly — use the **Executor framework**, **`CompletableFuture`**, and **virtual threads** (Java 21+).

## Raw threads (avoid for production)

```java
Thread t = new Thread(() -> System.out.println("running"));
t.start();
t.join();           // wait for it
```

Useful for learning. For real work, use a pool.

## ExecutorService

```java
ExecutorService pool = Executors.newFixedThreadPool(4);

Future<Integer> future = pool.submit(() -> {
    Thread.sleep(1000);
    return 42;
});

System.out.println(future.get());   // blocks until done

pool.shutdown();
pool.awaitTermination(10, TimeUnit.SECONDS);
```

Common factories:

```java
Executors.newFixedThreadPool(n);          // bounded
Executors.newCachedThreadPool();          // grows as needed (be careful)
Executors.newSingleThreadExecutor();      // serial executor
Executors.newScheduledThreadPool(n);      // delays + periodic
```

For Java 21+:

```java
Executors.newVirtualThreadPerTaskExecutor();   // virtual threads
```

## CompletableFuture — chainable async

```java
CompletableFuture<Integer> a = CompletableFuture.supplyAsync(() -> 1);
CompletableFuture<Integer> b = CompletableFuture.supplyAsync(() -> 2);

CompletableFuture<Integer> sum = a.thenCombine(b, Integer::sum);
sum.thenAccept(System.out::println);
```

Composition operators:

```java
.thenApply(fn)            // transform value
.thenCompose(fn)          // chain another future
.thenCombine(other, fn)   // combine two
.thenAccept(consumer)     // side effect
.exceptionally(throwable -> fallback)
.handle((value, ex) -> ...)
```

## Virtual threads (Java 21+)

Lightweight threads managed by the JVM. Millions per process; one blocked virtual thread doesn't block the underlying OS thread.

```java
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    for (int i = 0; i < 10_000; i++) {
        executor.submit(() -> {
            Thread.sleep(1000);
            return null;
        });
    }
}
```

Game-changer for I/O-heavy services. Code that was async with `CompletableFuture` can usually go back to synchronous style on virtual threads.

## Synchronization

```java
private final Object lock = new Object();

public void inc() {
    synchronized (lock) {
        count++;
    }
}
```

Or use `ReentrantLock` for advanced features:

```java
private final ReentrantLock lock = new ReentrantLock();

public void inc() {
    lock.lock();
    try { count++; }
    finally { lock.unlock(); }
}
```

For high-contention counters, `AtomicInteger`/`LongAdder` are lock-free and dramatically faster.

## Thread-safe collections

```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();
map.merge("key", 1, Integer::sum);          // atomic increment-or-insert
```

`computeIfAbsent`, `merge`, `compute` are all atomic.

## Pitfalls

- **Sleeping with held locks** — blocks others. Don't.
- **Forgetting `shutdown()`** — your JVM never exits.
- **Sharing mutable state without synchronization** — corruption is silent.
- **Using `Thread.stop()` / deprecated APIs** — they're gone for a reason.

## When NOT to thread

If your code is pure CPU work and finishes fast, threads add overhead. If it's I/O-heavy on Java 21+, virtual threads are the obvious win. For everything in between, measure.
