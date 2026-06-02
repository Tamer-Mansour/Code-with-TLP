# Common Process Pitfalls in Interviews

SystemC process questions appear frequently in hardware verification and virtual-platform engineering interviews. This lesson catalogues the most common mistakes, why they happen, and the one-line fix for each.

## Pitfall 1: Calling wait() Inside SC_METHOD

**Symptom:** Runtime fatal error — simulation aborts.

```cpp
// WRONG
SC_METHOD(my_method);
sensitive << clk.pos();

void my_method() {
    wait();   // ERROR: wait() not allowed in SC_METHOD
    out.write(in.read());
}
```

**Why it happens:** Developers migrate logic from `SC_THREAD` to `SC_METHOD` for performance without removing the `wait()` calls.

**Fix:** Convert to `SC_THREAD`, or restructure as a state machine using `next_trigger()`.

---

## Pitfall 2: Missing Sensitivity List on SC_METHOD

**Symptom:** Process never fires; output stuck at reset value.

```cpp
SC_CTOR(Foo) {
    SC_METHOD(compute);
    // FORGOT: sensitive << a << b;
}
```

**Fix:** Always verify every `SC_METHOD` has at least one signal on its sensitivity list. A common review checklist item.

---

## Pitfall 3: Incomplete Sensitivity List (Simulation/Synthesis Mismatch)

**Symptom:** Simulation passes, but synthesised hardware behaves differently.

```cpp
void compute() {
    out.write(a.read() + b.read() + c.read());
}

SC_CTOR(Foo) {
    SC_METHOD(compute);
    sensitive << a << b;   // c is missing!
}
```

RTL synthesis infers sensitivity from the function body; a change to `c` in simulation does not retrigger the method, but real hardware responds to it.

**Fix:** List every signal read inside the function.

---

## Pitfall 4: Infinite Loop Without wait() in SC_THREAD

**Symptom:** Simulation hangs at `sc_start()`, time never advances.

```cpp
void run() {
    while (req.read() == 0) {
        // spinning without yielding
    }
}
```

**Fix:**

```cpp
void run() {
    while (req.read() == 0) wait();  // yield on each iteration
    // ...
}
```

---

## Pitfall 5: Both-Edge Trigger Instead of Edge-Specific

**Symptom:** Clocked logic fires twice per clock period; counters increment by 2.

```cpp
SC_CTOR(Counter) {
    SC_THREAD(count);
    sensitive << clk;          // triggers on BOTH edges
}
// Should be:
//    sensitive << clk.pos();  // rising edge only
```

**Why it happens:** `clk` is an `sc_in<bool>`. Writing `sensitive << clk` makes the process sensitive to **any value change** — rising and falling. `.pos()` or `.neg()` selects a single edge.

---

## Pitfall 6: SC_THREAD That Returns (Terminates Early)

**Symptom:** Process fires once, then never again.

```cpp
void run() {
    wait();
    out.write(in.read());
    // function returns here — thread is dead
}
```

Hardware processes model continuous operation. Almost every `SC_THREAD` body should contain an infinite `while(true)` loop.

---

## Pitfall 7: Race Between Processes in the Same Delta Cycle

**Symptom:** Non-deterministic output; simulation result depends on registration order.

```cpp
// Process A writes signal X
// Process B reads signal X
// Both triggered in the same delta cycle
// B may read old or new value depending on scheduling order
```

**Fix:** Use `sc_signal` (which buffers writes until the next delta) rather than communicating through plain C++ variables. `sc_signal::write()` always makes the new value visible in the *next* delta cycle.

---

## Pitfall 8: Using next_trigger() in SC_THREAD or Registering a Function Twice

**next_trigger() in SC_THREAD:** Compile or runtime error. Use `wait(event)` instead — the two functions are mirror-image equivalents for their respective process types.

**Duplicate registration:** Each `SC_METHOD(func)` call creates a separate process instance, so the function fires twice per event. Combine sensitivity into one registration: `sensitive << a << b`.

---

## Quick-Reference Cheat Sheet

| Mistake | Process Type | Clue |
|---|---|---|
| Calling `wait()` | SC_METHOD | Runtime fatal |
| No sensitivity list | SC_METHOD | Output never changes |
| Incomplete sensitivity | SC_METHOD | Simulation/RTL mismatch |
| No `wait()` in loop | SC_THREAD | Simulation hangs |
| `sensitive << clk` | SC_THREAD | Double-edge trigger |
| Function returns | SC_THREAD | Process fires once |
| Ordering assumption | Either | Non-deterministic |

> **Interview answer:** The three most common SystemC process bugs are: (1) calling `wait()` in an `SC_METHOD` (fatal), (2) an incomplete sensitivity list causing simulation/synthesis mismatch, and (3) an `SC_THREAD` loop with no `wait()` that deadlocks the simulation. Always ask: "does every code path in my method have all its reads on the sensitivity list, and does every loop in my thread have at least one `wait()`?"
