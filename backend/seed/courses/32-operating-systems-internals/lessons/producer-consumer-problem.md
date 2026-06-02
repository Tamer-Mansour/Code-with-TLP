# The Producer-Consumer (Bounded Buffer) Problem

The producer-consumer problem is one of the most fundamental concurrency challenges in operating systems. It models the everyday scenario where one or more threads generate data (producers) while other threads consume that data (consumers), sharing a fixed-size buffer in between.

## The Setup

Imagine a pipeline: a web server thread parses incoming requests and places them into a queue, while worker threads pull requests out and process them. The queue has a maximum capacity — this is the **bounded buffer**.

- **Producer**: generates an item and places it in the buffer.
- **Consumer**: removes an item from the buffer and processes it.
- **Buffer**: a fixed-capacity shared queue (often a ring buffer).

## Why It's Hard

Three conditions must hold simultaneously:

| Condition | What breaks without it |
|-----------|------------------------|
| Mutual exclusion on the buffer | Two threads corrupt the same slot |
| Block when buffer is full | Producer overwrites unconsumed data |
| Block when buffer is empty | Consumer reads garbage or crashes |

Without synchronization, a producer and consumer accessing the buffer concurrently produce **race conditions** — the internal head/tail pointers get corrupted, items are lost, or the same item is consumed twice.

## The Naive (Broken) Approach

```cpp
// BROKEN — no synchronization
void producer() {
    while (true) {
        Item item = produce();
        if (count < BUFFER_SIZE)   // race: count may change between check and write
            buffer[in] = item;
        in = (in + 1) % BUFFER_SIZE;
        count++;
    }
}

void consumer() {
    while (true) {
        if (count > 0)             // race: same problem
            Item item = buffer[out];
        out = (out + 1) % BUFFER_SIZE;
        count--;
        consume(item);
    }
}
```

This code has multiple races: the check-then-act on `count` is not atomic, and `count++` / `count--` are not atomic on most hardware (they compile to read-modify-write sequences).

## The State That Needs Protecting

Three shared variables form the critical state:

```c
Item   buffer[BUFFER_SIZE];  // the circular array
int    in  = 0;              // next write slot
int    out = 0;              // next read slot
int    count = 0;            // items currently in buffer
```

Any thread touching `in`, `out`, or `count` is in a critical section. Additionally:

- A producer must **wait** if `count == BUFFER_SIZE`.
- A consumer must **wait** if `count == 0`.

## Common Pitfalls

- **Busy-waiting**: spinning on `count` burns CPU; the correct fix is to block on a condition variable or semaphore.
- **Lost wakeup**: checking the condition outside a lock means a signal can arrive before the thread sleeps, leaving it waiting forever.
- **Spurious wakeup**: a thread woken by the OS spuriously must re-check the condition (always use `while`, never `if`, around a wait).

## Real-World Analogies

- **Disk I/O queue**: the interrupt handler (producer) enqueues completed I/O events; the file-system thread (consumer) dequeues them.
- **Network receive ring**: the NIC DMA engine writes packets into a ring buffer; the kernel network stack reads them out.
- **Unix pipe**: the writing process is the producer; the reading process is the consumer; the pipe's internal buffer is bounded.

## Interview Answer

**Q: What is the producer-consumer problem?**

> A synchronization problem where producers add items to a bounded shared buffer and consumers remove them; the challenge is preventing races on the buffer, blocking producers when it is full, and blocking consumers when it is empty.
