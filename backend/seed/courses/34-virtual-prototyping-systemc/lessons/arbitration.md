# Arbitration Among Multiple Initiators

When two or more initiators (CPUs, DMAs, GPUs) try to use a shared bus simultaneously, the **arbiter** decides who goes first. Arbitration policy directly affects latency, fairness, and worst-case response time — all critical for real-time embedded systems.

## Why Arbitration Matters

Without arbitration, two simultaneous `b_transport()` calls on the same bus are a data race. The arbiter serializes them, models the wait time, and returns each caller's transaction in the correct order. Even in a TLM loose-timing model where ordering is approximate, the arbiter must prevent concurrent modification of shared mutable state.

## Common Arbitration Policies

| Policy | How it works | Best for |
|--------|-------------|----------|
| Fixed priority | Lower index always wins | Real-time: CPU > DMA > GPU |
| Round-robin | Each master gets a turn in order | Fair; prevents starvation |
| Weighted round-robin | Master i gets `w[i]` turns per round | Proportional bandwidth allocation |
| First-come-first-served | Request queue; FIFO order | General purpose |
| Least-recently-used | Grant to master idle longest | Starvation-free |

## Modeling Arbitration with a Mutex

The simplest correct model uses an `sc_mutex` to serialize access. Every initiator competes for the mutex; the winner executes its transaction while others wait.

```cpp
sc_core::sc_mutex bus_mutex_;

void b_transport(int initiator_id,
                 tlm::tlm_generic_payload& txn,
                 sc_time& delay) {
    bus_mutex_.lock();           // blocks until bus is free
    delay += BUS_ARBITRATION_NS; // model arbitration overhead
    // ... decode address and forward ...
    bus_mutex_.unlock();
}
```

`sc_mutex` gives first-come-first-served semantics. That is not round-robin, but it is correct and thread-safe.

## Round-Robin Arbitration

To implement true round-robin, maintain a `next_` counter and a per-master request queue:

```cpp
int next_ = 0;   // index of master to serve next

void arbitrate() {
    while (true) {
        wait(request_event_[next_]);   // wait for this master
        serve(next_);                  // run its transaction
        next_ = (next_ + 1) % NUM_MASTERS;
    }
}
```

In a TLM approximate-time model, this is typically implemented as an `SC_THREAD` that processes one queued transaction per arbitration slot:

```cpp
struct Request { tlm::tlm_generic_payload* txn; sc_time* delay;
                 sc_event* done; };
std::queue<Request> pending_[NUM_MASTERS];
```

## Modeling Latency for Losing Masters

When a master loses arbitration, it must wait. The simplest approach is to add the wait to the `delay` parameter rather than actually blocking simulation time (loose timing):

```cpp
// In an approximate model: losing master just pays extra delay
int wait_cycles = (NUM_MASTERS - 1) * BUS_CYCLE_NS;
delay += sc_time(wait_cycles, SC_NS);
```

In an approximately-timed (AT) model, use `wait(delay)` to consume real simulation time and accurately model contention.

## Fixed-Priority Example

```cpp
// Priority: master 0 > master 1 > master 2
int grant_priority(bool req[NUM_MASTERS]) {
    for (int i = 0; i < NUM_MASTERS; i++)
        if (req[i]) return i;
    return -1; // no requests
}
```

## Common Pitfalls

- **Forgetting starvation**: Fixed priority can starve low-priority masters under heavy load. Add a timeout that temporarily boosts priority.
- **sc_mutex vs. sc_semaphore**: `sc_mutex` is owned by the locking process; `sc_semaphore` can be released by a different process. Use the right one for your arbitration design.
- **Not accounting for arbitration latency**: Real arbiters take 1-2 cycles. Omitting this makes your bus appear faster than it is.
- **Concurrent queue access from multiple `SC_THREAD`s**: Protect the request queues with mutexes or use `sc_fifo`.

**Interview answer:** "A TLM bus arbiter serializes concurrent initiator transactions using an sc_mutex or a priority queue, models the wait time as added delay, and forwards each transaction in the chosen policy order — fixed priority, round-robin, or weighted — to prevent data races and reflect real contention latency."
