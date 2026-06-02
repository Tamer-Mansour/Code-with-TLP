# Barriers and Thread Rendezvous

A **barrier** is a synchronization point where every thread in a group must arrive before any of them is allowed to continue. It solves the **rendezvous** problem: coordinating a team of threads so that phase N completes entirely before phase N+1 begins.

## Why Barriers Exist

Parallel algorithms often have phases:

1. **Scatter**: each thread works on its own chunk of data.
2. **Gather**: results are merged (requires all chunks to be ready).
3. **Next phase**: computed from the merged result.

Without a barrier between steps 1 and 2, a fast thread might read a neighbor's chunk before the slow thread has written it.

## Barrier Using a Counter and a Mutex + Condition Variable

```c
typedef struct {
    int             count;       // threads not yet arrived
    int             total;       // total threads in the group
    pthread_mutex_t lock;
    pthread_cond_t  cv;
    int             generation;  // flips each barrier trip (reusable)
} Barrier;

void barrier_wait(Barrier *b) {
    pthread_mutex_lock(&b->lock);
    int gen = b->generation;

    b->count--;
    if (b->count == 0) {
        // Last thread to arrive
        b->count = b->total;
        b->generation++;              // advance generation
        pthread_cond_broadcast(&b->cv);
    } else {
        // Not the last — wait
        while (gen == b->generation)
            pthread_cond_wait(&b->cv, &b->lock);
    }
    pthread_mutex_unlock(&b->lock);
}
```

`pthread_cond_broadcast` wakes **all** waiting threads at once, which is the correct primitive here (unlike `signal`, which wakes only one).

## Barrier Using Semaphores (Little Book of Semaphores Pattern)

```c
// Two-phase barrier for N threads
// Phase 1: all arrive
sem_t arrive_mutex = 1;
sem_t turnstile1   = 0;   // closed initially
sem_t turnstile2   = 1;   // open initially
int count = 0;

void barrier(int n) {
    // --- Phase 1: wait for all to arrive ---
    sem_wait(&arrive_mutex);
    count++;
    if (count == n) {
        sem_wait(&turnstile2);   // close exit turnstile
        sem_post(&turnstile1);   // open entry turnstile
    }
    sem_post(&arrive_mutex);

    sem_wait(&turnstile1);       // all threads pass one by one
    sem_post(&turnstile1);       // reopen for next thread

    // --- critical point: all N threads are here ---

    // --- Phase 2: let all leave ---
    sem_wait(&arrive_mutex);
    count--;
    if (count == 0) {
        sem_wait(&turnstile1);   // close entry turnstile
        sem_post(&turnstile2);   // open exit turnstile
    }
    sem_post(&arrive_mutex);

    sem_wait(&turnstile2);
    sem_post(&turnstile2);
}
```

The two-turnstile design makes the barrier **reusable**: after all threads pass turnstile1, the second phase resets the state for the next use.

## POSIX Barrier API

POSIX provides barriers as a first-class primitive:

```c
#include <pthread.h>

pthread_barrier_t b;
pthread_barrier_init(&b, NULL, NUM_THREADS);

void* worker(void* arg) {
    // ... phase 1 work ...
    pthread_barrier_wait(&b);   // rendezvous
    // ... phase 2 work ...
    return NULL;
}
```

One thread receives `PTHREAD_BARRIER_SERIAL_THREAD` as the return value of `pthread_barrier_wait` — this designates it the "leader" for any post-barrier housekeeping.

## Worked Example: Parallel Prefix Sum

```
4 threads, array = [3, 1, 4, 2]

Phase 1: each thread stores its element locally
  T0=3, T1=1, T2=4, T3=2

BARRIER — all partial results written

Phase 2: each thread reads neighbors and computes prefix
  T0: prefix[0] = 3
  T1: prefix[1] = 3+1 = 4
  T2: prefix[2] = 3+1+4 = 8
  T3: prefix[3] = 3+1+4+2 = 10
```

Without the barrier, T1 might read T0's element before T0 has written it.

## Common Pitfalls

- **Using `signal` instead of `broadcast`**: only one thread is woken; the rest wait forever.
- **Non-reusable barrier**: a single-use barrier (counter never resets) causes the second invocation to pass without waiting.
- **Asymmetric thread counts**: if any thread never calls `barrier_wait`, all others block indefinitely.

## Interview Answer

**Q: What is a barrier and when do you use one?**

> A barrier is a synchronization primitive that blocks every thread in a group until all of them have arrived; it is used to separate phases of a parallel algorithm so that no thread starts phase N+1 before every thread finishes phase N.
