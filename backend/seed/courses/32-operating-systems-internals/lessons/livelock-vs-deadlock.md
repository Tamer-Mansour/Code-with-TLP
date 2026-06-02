# Livelock vs Deadlock

Deadlock and livelock both prevent progress, but for fundamentally different reasons. Understanding the distinction is critical for diagnosing concurrency bugs — the symptoms look similar (no useful work done) but the root causes and fixes differ entirely.

## What is Livelock?

In a **livelock**, processes are **actively running** — they are not blocked — but they keep reacting to each other in a way that prevents any of them from making forward progress. Each process politely defers to the others, and none ever proceeds.

**The classic human analogy:** Two people meet in a narrow corridor. Each steps aside to let the other pass. They both step the same direction, then the opposite direction, repeatedly — both moving, neither getting through.

## Code-Level Example

```python
import time, threading, random

resource_a = threading.Lock()
resource_b = threading.Lock()

def worker(name, first, second):
    while True:
        first.acquire()
        print(f"{name}: acquired first lock, trying second...")
        time.sleep(0.001)

        if second.acquire(blocking=False):  # non-blocking try
            print(f"{name}: acquired both — working!")
            second.release()
            first.release()
            break
        else:
            print(f"{name}: couldn't get second, backing off...")
            first.release()          # politely release and retry
            time.sleep(random.uniform(0, 0.01))  # random backoff

t1 = threading.Thread(target=worker, args=("T1", resource_a, resource_b))
t2 = threading.Thread(target=worker, args=("T2", resource_b, resource_a))
t1.start(); t2.start()
```

Without the `random.uniform` backoff, T1 and T2 will repeatedly acquire-release-acquire-release in lockstep — a livelock. Adding **randomised exponential backoff** is the canonical fix (the same technique used in Ethernet CSMA/CD).

## Side-by-Side Comparison

| Property | Deadlock | Livelock |
|----------|----------|----------|
| Process state | **Blocked** (waiting) | **Running** (but spinning) |
| CPU usage | Low (processes idle) | High (processes busy-looping) |
| Progress | None | None (but appears active) |
| Detectable by WFG? | Yes — cycle present | No — no blocked edges |
| Root cause | Circular wait for blocked resources | Circular courtesy / retry storm |
| Fix | Break one of the 4 conditions | Randomised backoff, priority ordering |

## Why Livelock is Harder to Diagnose

- CPU usage is high, masking the real problem.
- Thread states show "running" or "sleeping briefly" — not "blocked on mutex".
- The Wait-For Graph has no cycle because no process is actually blocked.
- Profilers show time spent in the retry/backoff loop rather than on any meaningful work.

## Real-World Occurrences

- **Network congestion control (early Ethernet):** Collisions caused all nodes to retry simultaneously, causing a livelock storm. Fixed by binary exponential backoff (random retry window).
- **Spinlock storms in the kernel:** Multiple cores spinning on the same spinlock with equally-timed retry intervals can oscillate without any making progress.
- **Distributed systems:** Multiple services retry a failed message simultaneously, overwhelming the target, causing it to fail again, repeating the cycle.

## Fixes and Prevention

1. **Randomised exponential backoff** — the most common fix. Add jitter so retries are unlikely to collide.
2. **Priority ordering** — designate one party as the "yielder"; it always backs off while the other proceeds.
3. **Central arbiter** — a lock manager serialises access, eliminating the courtesy dance.
4. **Timeout with escalation** — after N retries, escalate to a blocking wait rather than active spinning.

## Starvation: The Third Sibling

For completeness:

| Condition | Description |
|-----------|-------------|
| **Deadlock** | Circular wait; no process can proceed. |
| **Livelock** | Active but unproductive; processes keep reacting to each other. |
| **Starvation** | One or more processes are indefinitely postponed while others succeed. Progress *is* happening — just not for the starving process. |

## Interview Answer

> "In a deadlock, processes are blocked waiting for each other and consume no CPU. In a livelock, processes are actively running but keep deferring to each other in a cycle, consuming CPU without making progress. Livelock is harder to detect because no process is actually blocked. The standard fix is randomised exponential backoff."
