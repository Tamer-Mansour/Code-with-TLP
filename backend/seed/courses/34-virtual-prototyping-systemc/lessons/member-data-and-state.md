# Module Member Data and State

A SystemC module is a C++ class, so it can hold any C++ member data. This is one of SystemC's greatest strengths — and one of its most common sources of bugs. Knowing *what* to make a member, *how* to initialize it, and *when* it is safe to read or write determines whether your model is correct and reproducible.

## Categories of Module Members

| Category | Examples | Initialized In |
|---|---|---|
| Ports | `sc_in<bool> clk` | Declared; bound in parent constructor |
| Internal signals | `sc_signal<int> pipe_reg` | Declared; driven by processes |
| Child modules | `Alu alu` | Initializer list |
| Configuration | `int width, depth` | Constructor parameter / initializer list |
| Behavioral state | `int counter`, `bool busy` | Initializer list or `start_of_simulation` |
| Buffers/queues | `std::queue<Packet> q` | Default-constructed or initializer list |

## Ports Are Not Signals

A common confusion: `sc_in<T>` and `sc_out<T>` are *port objects*, not signal objects. They hold no value themselves — they are references into an `sc_signal<T>` that lives somewhere in the parent or at the same level. Reading an unbound port is undefined behavior.

```cpp
SC_MODULE(Adder) {
    sc_in<int>  a, b;
    sc_out<int> sum;

    SC_CTOR(Adder) {
        SC_METHOD(compute);
        sensitive << a << b;
    }

    void compute() {
        sum.write(a.read() + b.read());  // reads from the bound sc_signal
    }
};
```

## Behavioral State Variables

Behavioral state (registers, FSM state, packet counters) should be plain C++ types, not `sc_signal`. Use `sc_signal` only when other processes must be *sensitive* to a value change. Otherwise a plain member variable is faster and simpler:

```cpp
SC_MODULE(Uart) {
    int      tx_shift_reg;  // only one process touches this — plain member
    sc_signal<bool> tx_ready;  // other modules read this — must be sc_signal

    SC_CTOR(Uart) : tx_shift_reg(0) {
        SC_THREAD(transmit);
    }
    // ...
};
```

## Initialization Rules

**Initializer list** is the correct place for member initialization:

```cpp
SC_MODULE(Buffer) {
    int depth;
    bool overflow_seen;

    Buffer(sc_module_name nm, int d)
        : sc_module(nm), depth(d), overflow_seen(false)
    { /* process registration here */ }
};
```

Assigning inside the constructor body is technically legal but can leave members in an undefined state briefly during construction if an exception fires.

## Resettable State and start_of_simulation

If your model needs a clean reset between multiple simulation runs (e.g., in a regression loop), initialize behavioral state inside `start_of_simulation()` rather than only in the constructor:

```cpp
void start_of_simulation() override {
    counter = 0;
    busy    = false;
}
```

The constructor runs once at elaboration; `start_of_simulation` runs before each `sc_start()` in a multi-run scenario.

## Shared State and Race Conditions

SystemC processes run in a cooperative, event-driven scheduler. Within a single delta cycle, two `SC_METHOD` processes can both run — but not simultaneously. However, if both write to the same plain C++ member variable, the result depends on evaluation order, which is implementation-defined.

Safe patterns:

- **One writer, multiple readers** — only one process writes a plain member; others only read it.
- **Use `sc_signal<T>`** when multiple processes must write or when readers need to be notified.
- **Use `sc_mutex` or `sc_semaphore`** inside `SC_THREAD` processes that share resources.

## Memory Ownership for Dynamically Allocated Members

If you `new` a buffer or a subordinate object in the constructor, the module owns it. Prefer RAII wrappers:

```cpp
SC_MODULE(DmaEngine) {
    std::unique_ptr<uint8_t[]> internal_buf;

    DmaEngine(sc_module_name nm, size_t sz)
        : sc_module(nm), internal_buf(new uint8_t[sz]) {}
};
```

Avoid raw owning pointers — they will leak if the module is destroyed before the simulation ends.

## Common Pitfalls

- **Reading a port before binding is complete.** Causes a null-pointer dereference inside the port's channel reference.
- **Using `sc_signal` for private state that no other process observes.** Wastes delta-cycle overhead; use a plain member.
- **Forgetting to initialize behavioral state.** C++ does not zero-initialize non-static members; uninitialized `int` members have indeterminate values.

> **Interview answer:** Module members fall into ports (interface to other modules), internal `sc_signal` channels (for inter-process communication within the module), and plain C++ data (private behavioral state). Plain members are initialized in the constructor initializer list; state that must be reset between simulation runs goes in `start_of_simulation`. Use `sc_signal` only when other processes need to observe a value change, not for private state.
