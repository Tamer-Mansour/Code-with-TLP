# Synchronization and Locks

When multiple threads share mutable state, you need to ensure **visibility** (changes made by one thread are seen by others) and **atomicity** (operations complete without interference). Java provides several tools for this.

## The `synchronized` keyword

The simplest tool: only one thread at a time can enter a `synchronized` block or method.

```java
public class Counter {
    private int value = 0;

    public synchronized void increment() {
        value++;   // read-modify-write is now atomic
    }

    public synchronized int get() {
        return value;
    }
}
```

For finer control, synchronize on an explicit lock object:

```java
public class SafeList<T> {
    private final Object lock = new Object();
    private final List<T> list = new ArrayList<>();

    public void add(T item) {
        synchronized (lock) {
            list.add(item);
        }
    }

    public int size() {
        synchronized (lock) {
            return list.size();
        }
    }
}
```

## `volatile`

Guarantees **visibility** only — not atomicity. Use when one thread writes and others just read, and you don't need compound operations.

```java
class Worker implements Runnable {
    private volatile boolean running = true;

    public void stop() { running = false; }

    @Override
    public void run() {
        while (running) {
            // do work
        }
    }
}
```

Without `volatile`, the JVM might cache `running` in a register and the loop never exits.

## `java.util.concurrent.locks`

`ReentrantLock` gives you everything `synchronized` does, plus:
- Tryable acquisition (`tryLock()`)
- Interruptible locking
- Separate `Condition` objects (like `wait`/`notify` but per-condition)

```java
import java.util.concurrent.locks.*;

public class BoundedBuffer<T> {
    private final Lock lock = new ReentrantLock();
    private final Condition notFull  = lock.newCondition();
    private final Condition notEmpty = lock.newCondition();
    private final Queue<T> queue = new LinkedList<>();
    private final int capacity;

    public BoundedBuffer(int capacity) { this.capacity = capacity; }

    public void put(T item) throws InterruptedException {
        lock.lock();
        try {
            while (queue.size() == capacity) notFull.await();
            queue.add(item);
            notEmpty.signal();
        } finally {
            lock.unlock();   // always unlock in finally!
        }
    }

    public T take() throws InterruptedException {
        lock.lock();
        try {
            while (queue.isEmpty()) notEmpty.await();
            T item = queue.poll();
            notFull.signal();
            return item;
        } finally {
            lock.unlock();
        }
    }
}
```

## Atomic classes

`java.util.concurrent.atomic` provides lock-free thread-safe primitives built on hardware CAS (compare-and-swap):

```java
import java.util.concurrent.atomic.*;

AtomicInteger counter = new AtomicInteger(0);
counter.incrementAndGet();          // atomic ++
counter.compareAndSet(5, 10);       // CAS: if value==5, set to 10

AtomicLong, AtomicBoolean, AtomicReference<T>
LongAdder  // better than AtomicLong under high contention
```

## Common pitfalls

| Mistake | Consequence |
|---------|-------------|
| Forgetting `synchronized` on getter as well as setter | Stale reads |
| Locking on `this` in a public class | Callers can grab the same lock externally |
| Calling `wait()` outside a `while` loop | Spurious wakeups cause bugs |
| Using `volatile` for compound check-then-act | Not atomic — use `AtomicReference` or locks |
| Holding locks during I/O | Reduces throughput; other threads starve |

## Quick rule of thumb

- **Immutable objects** — no synchronization needed.
- **Confined objects** — used by one thread only; no synchronization needed.
- **`synchronized`** — easy, good enough for low-contention cases.
- **`Lock` / `Condition`** — when you need tryLock or per-condition signaling.
- **Atomic classes** — counter/flag scenarios without locks.
- **`java.util.concurrent` collections** — `ConcurrentHashMap`, `CopyOnWriteArrayList` for shared data structures.
