# Why Signal Writes Take Effect Next Delta

A consistent point of confusion for engineers new to SystemC is this: why doesn't a signal update immediately when you call `write()`? The answer lies at the heart of how the kernel guarantees deterministic, race-free simulation.

## The Fundamental Rule

When a process calls `sig.write(value)`, the new value is stored in a **pending buffer** associated with the signal. The current value of the signal — what `sig.read()` returns — does not change until the **update phase** of the current delta cycle.

```cpp
void example() {
    std::cout << sig.read() << "\n";  // prints: 0
    sig.write(1);
    std::cout << sig.read() << "\n";  // STILL prints: 0 (write is pending)
    // After this method returns, update phase fires, sig becomes 1
}
```

## Why This Design?

### Guaranteeing Consistent Reads

Suppose two processes are both sensitive to signal A and both run in the same evaluate phase. Both compute a new value for signal B. If writes were immediate:

- Process 1 writes B = 1, then Process 2 reads B = 1 (wrong — it should see B's old value).
- Result: output depends on run order, which is undefined.

With deferred writes, both processes read the same old value of B regardless of which runs first. The new value is committed only after both have completed.

### Mirroring Real Hardware

Real digital logic operates the same way. A flip-flop's output Q does not change the moment its D input changes — it changes on the clock edge, after setup/hold time. The evaluate-update model captures this "all changes happen simultaneously at a clock boundary" semantics.

## Worked Example: Two Inverters in a Ring

```cpp
SC_MODULE(Ring) {
    sc_signal<bool> a, b;

    void inv_a() { a.write(!b.read()); }
    void inv_b() { b.write(!a.read()); }

    SC_CTOR(Ring) {
        SC_METHOD(inv_a); sensitive << b;
        SC_METHOD(inv_b); sensitive << a;
    }
};
```

Starting with `a=0, b=0`:

| Delta | Evaluate | Pending write | Update result | New trigger |
|---|---|---|---|---|
| 0 | init: inv_a and inv_b run | a=1, b=1 | a=1, b=1 | both again |
| 1 | inv_a reads b=1 → a=0; inv_b reads a=1 → b=0 | a=0, b=0 | a=0, b=0 | both again |
| 2 | inv_a reads b=0 → a=1; inv_b reads a=0 → b=1 | a=1, b=1 | back to delta 1 | oscillates |

This model oscillates endlessly — an infinite delta loop. It is a useful demonstration that the deferred-write rule prevents inconsistency but does not prevent unbounded oscillation. Real models must ensure convergence.

## The `sc_signal` vs `sc_buffer` Distinction

By default, `sc_signal` only notifies downstream processes if the new value **differs** from the current value. This prevents spurious activations.

`sc_buffer` notifies on every write, even if the value is the same:

```cpp
sc_signal<int> sig;    // notifies only on value change
sc_buffer<int> buf;    // notifies on every write
```

Use `sc_buffer` when your downstream process must react to every write event, even repeated same-value writes (e.g., pulse counting).

## Immediate Ports and `sc_signal_resolved`

`sc_signal_resolved` supports multiple drivers (wired-OR / wired-AND semantics). Each driver's write goes into a per-driver pending buffer. During update, all drivers' values are resolved (e.g., using four-state logic) and the result is committed.

## Common Pitfalls

- **Testing the written value before update**: within the same process, calling `write()` then `read()` on the same signal always returns the old value.
- **Chained same-delta updates**: process A writes sig1 → update → process B writes sig2 → update. This takes two delta cycles, not one. Plan your pipeline depth accordingly.
- **Forgetting SC_ZERO_TIME vs immediate**: immediate `notify()` fires in the same evaluate phase; `notify(SC_ZERO_TIME)` fires after the current update phase completes. Choose the right one for your ordering requirements.

## Interview Answer

> "Signal writes in SystemC are deferred — they go into a pending buffer and are committed only during the update phase, after all processes in the current evaluate phase have completed. This ensures every process in one evaluate step reads a consistent snapshot of the previous state, eliminating data races between concurrently running processes."
