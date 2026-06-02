# Solving Producer-Consumer With Semaphores

Semaphores provide an elegant, classical solution to the producer-consumer problem. The key insight is that you need **three** semaphores: two counting semaphores to track available slots and available items, plus one binary semaphore for mutual exclusion on the buffer itself.

## The Three Semaphores

| Semaphore | Initial value | Meaning |
|-----------|--------------|---------|
| `empty`   | `BUFFER_SIZE` | Number of empty slots in the buffer |
| `full`    | `0`           | Number of filled slots in the buffer |
| `mutex`   | `1`           | Binary lock guarding buffer access |

- `empty` counts how many slots the producer can write into.
- `full` counts how many items the consumer can read.
- `mutex` ensures only one thread modifies the buffer at a time.

## The Solution

```c
#define BUFFER_SIZE 8

Item  buffer[BUFFER_SIZE];
int   in  = 0, out = 0;

sem_t empty;   // initialized to BUFFER_SIZE
sem_t full;    // initialized to 0
sem_t mutex;   // initialized to 1

void producer() {
    while (true) {
        Item item = produce_item();

        sem_wait(&empty);   // block if no empty slots
        sem_wait(&mutex);   // enter critical section

        buffer[in] = item;
        in = (in + 1) % BUFFER_SIZE;

        sem_post(&mutex);   // leave critical section
        sem_post(&full);    // signal one more item available
    }
}

void consumer() {
    while (true) {
        sem_wait(&full);    // block if no items
        sem_wait(&mutex);   // enter critical section

        Item item = buffer[out];
        out = (out + 1) % BUFFER_SIZE;

        sem_post(&mutex);   // leave critical section
        sem_post(&empty);   // signal one more slot available

        consume_item(item);
    }
}
```

## Step-by-Step Trace

Assume `BUFFER_SIZE = 2`, one producer, one consumer.

```
Initial: empty=2, full=0, mutex=1, buffer=[]

Producer runs:
  sem_wait(empty) → empty=1
  sem_wait(mutex) → mutex=0
  buffer[0] = A;  in=1
  sem_post(mutex) → mutex=1
  sem_post(full)  → full=1

Consumer runs:
  sem_wait(full)  → full=0
  sem_wait(mutex) → mutex=0
  item = buffer[0] (A);  out=1
  sem_post(mutex) → mutex=1
  sem_post(empty) → empty=2
```

## Critical Ordering Rule

The `mutex` lock must be acquired **after** `empty`/`full`, never before:

```c
// DEADLOCK — wrong order!
sem_wait(&mutex);
sem_wait(&empty);   // blocks here while holding mutex
                    // consumer can never acquire mutex to post full
```

If a producer holds `mutex` and then blocks on `empty`, no consumer can ever run `sem_post(&empty)` because it would need `mutex` first. Classic deadlock.

## Condition Variable Alternative (POSIX)

Modern code often prefers condition variables paired with a mutex:

```c
pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t  not_full  = PTHREAD_COND_INITIALIZER;
pthread_cond_t  not_empty = PTHREAD_COND_INITIALIZER;
int count = 0;

void producer() {
    pthread_mutex_lock(&lock);
    while (count == BUFFER_SIZE)          // always 'while', not 'if'
        pthread_cond_wait(&not_full, &lock);
    buffer[in] = produce_item();
    in = (in + 1) % BUFFER_SIZE;
    count++;
    pthread_cond_signal(&not_empty);
    pthread_mutex_unlock(&lock);
}
```

The `while` loop around `pthread_cond_wait` guards against spurious wakeups — the OS may unblock a thread for reasons unrelated to the signal.

## Common Pitfalls

- **Forgetting `mutex`**: two producers can corrupt `in` simultaneously even if the counting semaphores are correct.
- **Signaling before releasing `mutex`**: valid but can cause a "thundering herd" if many threads wake up; signal after releasing to allow the woken thread to acquire immediately.
- **Using a single semaphore**: a single semaphore cannot simultaneously represent "buffer not full" and "buffer not empty" as separate blocking conditions.

## Interview Answer

**Q: How do you solve producer-consumer with semaphores?**

> Use three semaphores: `empty` (initialized to buffer size) to block producers when full, `full` (initialized to 0) to block consumers when empty, and `mutex` (binary, initialized to 1) for mutual exclusion; always acquire `empty`/`full` before `mutex` to avoid deadlock.
