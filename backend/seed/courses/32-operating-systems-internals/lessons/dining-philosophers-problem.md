# The Dining Philosophers Problem

The dining philosophers problem, introduced by Dijkstra in 1965, is the canonical illustration of **deadlock** and **livelock** in concurrent systems. It is simple to state, subtle to solve, and a staple of operating systems interviews.

## The Setup

Five philosophers sit around a circular table. Between each pair of adjacent philosophers lies a single fork (chopstick). To eat, a philosopher needs **both** the fork to their left and the fork to their right.

```
        [P0]
    fork4    fork0
  [P4]          [P1]
    fork3    fork1
        [P3]--fork2--[P2]
```

Each philosopher alternates between thinking and eating:

```c
void philosopher(int i) {
    while (true) {
        think();
        pick_up_forks(i);   // acquire left fork, then right fork
        eat();
        put_down_forks(i);
    }
}
```

There are 5 forks and 5 philosophers. Each fork is modeled as a mutex (binary semaphore).

## The Deadlock Scenario

The naive approach: pick up left fork, then right fork.

```c
void pick_up_forks(int i) {
    sem_wait(&fork[i]);              // left fork
    sem_wait(&fork[(i+1) % 5]);     // right fork
}
```

If all five philosophers become hungry simultaneously and each picks up their left fork, every philosopher holds one fork and waits for the fork held by their right neighbor. A circular wait — the fourth condition for deadlock — is formed. No one can proceed.

## Solution 1: Allow at Most N-1 Philosophers at the Table

Introduce a "room" semaphore initialized to 4. At most four philosophers can compete for forks at once, guaranteeing at least one can always complete.

```c
sem_t room = 4;   // one fewer than the number of philosophers

void pick_up_forks(int i) {
    sem_wait(&room);
    sem_wait(&fork[i]);
    sem_wait(&fork[(i+1) % 5]);
}

void put_down_forks(int i) {
    sem_post(&fork[(i+1) % 5]);
    sem_post(&fork[i]);
    sem_post(&room);
}
```

Why it works: with at most 4 philosophers competing, at least one pair of adjacent forks is always free. The holding pair can eat and release, breaking any potential cycle.

## Solution 2: Asymmetric Fork Ordering

Break the circular dependency by making one philosopher pick up forks in a different order.

```c
void pick_up_forks(int i) {
    if (i % 2 == 0) {
        sem_wait(&fork[i]);              // even: left first
        sem_wait(&fork[(i+1) % 5]);
    } else {
        sem_wait(&fork[(i+1) % 5]);     // odd: right first
        sem_wait(&fork[i]);
    }
}
```

By making philosopher 0 (or any one philosopher) pick up the higher-numbered fork first, the circular wait condition is broken. At least one pair of adjacent philosophers acquires forks in opposite orders, preventing a full cycle.

## Solution 3: Monitor / State Machine

Each philosopher has a state: `THINKING`, `HUNGRY`, `EATING`. A philosopher starts eating only when both neighbors are not eating.

```c
typedef enum { THINKING, HUNGRY, EATING } State;
State state[5];
sem_t mutex    = 1;
sem_t s[5];           // one semaphore per philosopher, init 0

void test(int i) {
    if (state[i] == HUNGRY &&
        state[(i+4) % 5] != EATING &&
        state[(i+1) % 5] != EATING) {
        state[i] = EATING;
        sem_post(&s[i]);
    }
}

void pick_up_forks(int i) {
    sem_wait(&mutex);
    state[i] = HUNGRY;
    test(i);
    sem_post(&mutex);
    sem_wait(&s[i]);   // block if test() didn't grant permission
}

void put_down_forks(int i) {
    sem_wait(&mutex);
    state[i] = THINKING;
    test((i+4) % 5);   // try to wake left neighbor
    test((i+1) % 5);   // try to wake right neighbor
    sem_post(&mutex);
}
```

This is deadlock-free and starvation-free (assuming a fair semaphore).

## Livelock: The Other Failure Mode

A livelock occurs when each philosopher picks up their left fork, detects the right fork is unavailable, puts the left fork back, waits a moment, and tries again — forever. Everyone is active, but no one makes progress.

Livelock is often introduced by "polite" retry logic added to avoid deadlock without a proper solution.

## Summary of Solutions

| Solution | Deadlock-free | Starvation-free | Complexity |
|----------|--------------|----------------|------------|
| Naive (broken) | No | No | Low |
| Room semaphore | Yes | Possible | Low |
| Asymmetric ordering | Yes | Possible | Low |
| Monitor/state machine | Yes | Yes | High |

## Interview Answer

**Q: What is the dining philosophers problem and how do you solve it?**

> Five philosophers share five forks; eating requires two adjacent forks. The naive solution deadlocks when all grab their left fork simultaneously. Safe solutions include limiting concurrent diners to N-1, using asymmetric fork-pickup order to break circular wait, or a monitor that only grants forks when both neighbors are not eating.
