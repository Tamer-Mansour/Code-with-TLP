# The wait() Statement and Suspension

`wait()` is the mechanism that allows an `SC_THREAD` to **yield control back to the kernel** and resume later. It is the single most important function for writing multi-cycle hardware models.

## What Happens When wait() Is Called

1. The current thread's execution context (stack, program counter, local variables) is **saved**.
2. Control returns to the **SystemC scheduler**.
3. The scheduler runs other ready processes (and advances time if needed).
4. When the specified condition is met, the thread is placed back on the runnable queue.
5. On the next dispatch, the thread resumes at the **statement immediately after** the `wait()` call.

This is cooperative multitasking — the thread chooses when to yield, not the OS.

## wait() Signatures

```cpp
// 1. Wait for next event on static sensitivity list
wait();

// 2. Wait for a specific event
wait(clk.posedge_event());

// 3. Wait for a set of events (OR)
wait(req.value_changed_event() | ack.value_changed_event());

// 4. Wait for a fixed simulated time
wait(10, SC_NS);    // 10 nanoseconds
wait(1, SC_US);     // 1 microsecond
wait(5, SC_CLK_PERIOD);   // if you define that unit

// 5. Wait for a timeout OR an event (whichever comes first)
wait(100, SC_NS, done.posedge_event());

// 6. Wait for N firings of the static sensitivity list
wait(3);   // fire three times before resuming
```

## Time Units in SystemC

| Constant | Meaning |
|---|---|
| `SC_FS` | femtoseconds |
| `SC_PS` | picoseconds |
| `SC_NS` | nanoseconds |
| `SC_US` | microseconds |
| `SC_MS` | milliseconds |
| `SC_SEC` | seconds |

## Worked Example: Debounce Filter

```cpp
SC_MODULE(Debounce) {
    sc_in<bool>  raw_btn;
    sc_out<bool> clean_btn;

    SC_CTOR(Debounce) {
        SC_THREAD(debounce_proc);
        sensitive << raw_btn.value_changed_event();
    }

    void debounce_proc() {
        clean_btn.write(0);
        while (true) {
            wait();                        // wait for any button change
            bool level = raw_btn.read();
            wait(20, SC_MS);               // wait 20 ms (debounce window)
            if (raw_btn.read() == level) { // still the same? stable.
                clean_btn.write(level);
            }
        }
    }
};
```

The debounce logic reads naturally as a sequence: detect edge → wait → confirm → output. This would be far more complex as an `SC_METHOD` with explicit timers.

## Checking Which Event Fired (Timeout vs Event)

When using the combined `wait(time, event)` form you often need to know which ended the wait:

```cpp
sc_event ack_event;

void master() {
    req.write(1);
    wait(50, SC_NS, ack_event);   // timeout or ack

    if (sc_time_stamp() < timeout_deadline) {
        // ack came before timeout
    } else {
        // timeout: handle error
        req.write(0);
    }
}
```

A cleaner alternative is to check whether the signal has the expected value after the wait returns.

## wait() Is Illegal in SC_METHOD

Calling `wait()` inside an `SC_METHOD` causes a fatal runtime error:

```
Error: (E519) wait() is not allowed in SC_METHOD processes
```

If you find yourself needing `wait()` in a method, convert it to an `SC_THREAD`.

## Common Pitfall: Waiting on the Wrong Edge

```cpp
sensitive << clk;           // fires on BOTH edges
// vs
sensitive << clk.pos();     // fires only on rising edge
```

Using `sensitive << clk` without `.pos()` or `.neg()` means the thread wakes twice per clock cycle, which breaks cycle-accurate models. Always specify the edge explicitly.

## Delta Cycles and wait(SC_ZERO_TIME)

`wait(SC_ZERO_TIME)` suspends the thread for zero simulated time but forces a **delta cycle**. This lets other processes that were triggered in the current delta run first, then the thread resumes. Use it to resolve ordering issues between cooperating processes.

> **Interview answer:** `wait()` suspends an `SC_THREAD`, saves its call stack, and returns control to the SystemC scheduler. It can wait for a specific event, a timeout, or N firings of the sensitivity list. It is illegal in `SC_METHOD`. The most common pitfall is using `sensitive << clk` instead of `clk.pos()`, causing double-edge triggers.
