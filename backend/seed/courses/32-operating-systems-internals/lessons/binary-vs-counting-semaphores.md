# Semaphores: Binary vs Counting

A **semaphore** is a synchronization primitive invented by Edsger Dijkstra in 1965. Unlike a mutex, a semaphore is fundamentally a **counter** — an integer that threads can increment or decrement atomically. The value of that counter determines whether a thread proceeds or blocks.

## The Two Variants

| Property | Binary Semaphore | Counting Semaphore |
|---|---|---|
| Counter range | 0 or 1 only | 0 to N (N set at creation) |
| Primary use | Mutual exclusion / signaling | Controlling access to N resources |
| Unlocking thread | Any thread can signal | Any thread can signal |
| Initial value | 1 (or 0 for signaling) | Typically N (resource count) |

## Binary Semaphore

A binary semaphore's counter can only be 0 (locked) or 1 (free). When it is initialized to 1, it behaves similarly to a mutex — only one thread proceeds at a time.

```c
#include <semaphore.h>

sem_t bin_sem;
sem_init(&bin_sem, 0, 1);  // initial value = 1

// Thread A
sem_wait(&bin_sem);   // decrement → 0; proceed
// critical section
sem_post(&bin_sem);   // increment → 1; wake a waiter
```

The crucial difference from a mutex: **any thread** can call `sem_post`, not just the one that called `sem_wait`. This makes binary semaphores useful for **signaling** between threads (producer notifies consumer) without the ownership constraint of a mutex.

## Counting Semaphore

A counting semaphore is initialized to N, representing N available slots of some shared resource (e.g., N database connections, N buffer slots).

```c
sem_t pool_sem;
sem_init(&pool_sem, 0, 5);  // 5 connections available

void use_connection() {
    sem_wait(&pool_sem);    // acquire one slot; blocks if all 5 are in use
    // use the connection
    sem_post(&pool_sem);    // release the slot
}
```

Every `sem_wait` decrements the counter; every `sem_post` increments it. When the counter reaches 0, further `sem_wait` callers block until another thread posts.

## Classic Producer-Consumer with a Counting Semaphore

```c
#define BUFFER_SIZE 10

sem_t empty;  // counts empty slots
sem_t full;   // counts filled slots

sem_init(&empty, 0, BUFFER_SIZE);
sem_init(&full,  0, 0);

void producer() {
    while (1) {
        item_t item = produce();
        sem_wait(&empty);   // wait for an empty slot
        enqueue(item);
        sem_post(&full);    // signal that a slot is now full
    }
}

void consumer() {
    while (1) {
        sem_wait(&full);    // wait for a filled slot
        item_t item = dequeue();
        sem_post(&empty);   // signal that a slot is now empty
        consume(item);
    }
}
```

This pattern uses two counting semaphores to coordinate flow without any explicit busy-wait.

## Common Pitfalls

- **Forgetting to post** after a wait causes other threads to block indefinitely (semaphore starvation).
- **Extra posts** push the counter above the intended maximum, allowing more concurrent accesses than designed.
- **Using a binary semaphore as a mutex** is tempting but dangerous: since there is no ownership, any thread can inadvertently unlock it, breaking invariants.
- **Priority inversion** can occur: a high-priority thread waits on a semaphore held indirectly by a low-priority thread with no priority inheritance protocol.

## When to Choose Each

- **Binary semaphore (value = 0, signaling pattern):** one thread signals another that an event has occurred (interrupt-to-thread notification, event flags).
- **Binary semaphore (value = 1, mutex-like):** lightweight critical section when ownership rules are not needed.
- **Counting semaphore:** throttle access to a fixed pool of resources; implement producer-consumer flow control.

> **Interview answer:** A binary semaphore is a 0/1 counter used for mutual exclusion or signaling; a counting semaphore starts at N and throttles concurrent access to N resources. Unlike a mutex, a semaphore has no ownership — any thread can signal it.
