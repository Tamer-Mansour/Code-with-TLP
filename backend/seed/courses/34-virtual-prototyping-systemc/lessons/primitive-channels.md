# Primitive vs Hierarchical Channels

SystemC channels come in two architectural flavors: **primitive** and **hierarchical**. The distinction affects how they interact with the simulation kernel, whether they can contain processes, and how they handle concurrent access.

## Primitive Channels

A primitive channel inherits from `sc_prim_channel`. It participates directly in the delta-cycle update mechanism via the `update()` method, which the kernel calls once per delta cycle after all processes have run.

```cpp
class my_signal : public sc_prim_channel,
                  public sc_signal_inout_if<int> {
    int current_val = 0;
    int next_val    = 0;
    sc_event value_changed;

public:
    // Called by writers — queues but doesn't commit yet
    void write(const int& v) override {
        next_val = v;
        request_update();    // tells kernel to call update() this delta
    }

    const int& read() const override { return current_val; }

    // Called by kernel at end of delta — now commit the write
    void update() override {
        if (next_val != current_val) {
            current_val = next_val;
            value_changed.notify();    // wake sensitive processes
        }
    }

    const sc_event& value_changed_event() const override {
        return value_changed;
    }
};
```

### Key Properties of Primitive Channels

- **No child processes or modules**: they are leaf objects in the module hierarchy.
- **`request_update()` / `update()`**: the two-phase write mechanism guarantees determinism — all reads in an evaluation phase see the *old* value; only after `update()` does the new value become visible.
- **Lightweight**: minimal overhead; the kernel batches all pending updates together.

### Standard Primitive Channels

| Channel | Description |
|---|---|
| `sc_signal<T>` | Single-value wire with delta buffering |
| `sc_buffer<T>` | Like `sc_signal` but notifies on every write |
| `sc_fifo<T>` | Bounded blocking FIFO queue |
| `sc_mutex` | Binary lock for shared resource protection |
| `sc_semaphore` | Counting semaphore |

## Hierarchical Channels

A hierarchical channel inherits from `sc_channel` (which itself inherits from `sc_module`). Because it is a module, it **can contain processes, submodules, and other channels**.

```cpp
class ArbiterChannel : public sc_channel {
    sc_in_clk        clk;
    sc_signal<bool>  grant[4];
    int              current_owner = -1;

    SC_CTOR(ArbiterChannel) {
        SC_METHOD(arbitrate);
        sensitive << clk.pos();
    }

    void arbitrate() {
        // round-robin logic driving grant signals
    }
public:
    // expose interface methods to ports
};
```

### Key Properties of Hierarchical Channels

- **Can contain processes**: use `SC_METHOD`, `SC_THREAD` inside the channel.
- **Full module features**: ports, child modules, local signals are all allowed.
- **More complex**: the update phase is not directly involved; processes handle timing internally.
- **Typical uses**: bus models (AHB, AXI), network-on-chip routers, complex arbiters.

## Side-by-Side Comparison

| Feature | Primitive (`sc_prim_channel`) | Hierarchical (`sc_channel`) |
|---|---|---|
| Can contain processes | No | Yes |
| `request_update()` / `update()` | Yes | No |
| Can contain child modules | No | Yes |
| Simulation overhead | Low | Higher |
| Typical complexity | Simple (signal, FIFO) | Complex (bus model, router) |
| VCD tracing | Easy | Possible but manual |

## When to Choose Each

```
Is the channel a simple data pipe or lock?
    YES → sc_prim_channel (sc_signal, sc_fifo, sc_mutex)

Does the channel need internal arbitration logic or a state machine?
    YES → sc_channel (hierarchical)

Is performance critical (millions of events per second)?
    YES → sc_prim_channel preferred

Are you modeling a complex interconnect (AXI, PCIe)?
    YES → sc_channel
```

## Worked Example: Simple Hierarchical Bus

```cpp
class SimpleBus : public sc_channel {
public:
    sc_in<sc_uint<32>>  addr;
    sc_in<sc_uint<32>>  wdata;
    sc_out<sc_uint<32>> rdata;
    sc_in<bool>         write_en;
    sc_in_clk           clk;

private:
    std::map<uint32_t, uint32_t> mem;

    SC_CTOR(SimpleBus) {
        SC_METHOD(access);
        sensitive << clk.pos();
    }

    void access() {
        if (write_en.read())
            mem[addr.read()] = wdata.read();
        else
            rdata.write(mem[addr.read()]);
    }
};
```

This channel encapsulates bus behavior, including its own process, which would be impossible with a primitive channel.

## Common Pitfalls

1. **Calling `request_update()` in a hierarchical channel**: it is not available; use processes instead.
2. **Adding processes to a primitive channel**: `sc_prim_channel` has no process-spawning macros — this is a compile error.
3. **Delta storm in primitive channels**: a channel that always calls `request_update()` even when the value has not changed will cause the simulator to loop indefinitely.

> **Interview answer:** Primitive channels (`sc_prim_channel`) participate in the kernel's two-phase update mechanism and are restricted to leaf objects with no processes, making them lightweight and deterministic; hierarchical channels (`sc_channel`) are full modules that can contain processes and submodules, enabling complex on-chip interconnect modeling at the cost of higher overhead.
