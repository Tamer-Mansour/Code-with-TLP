# Instantiating and Connecting Submodules

Building a realistic virtual prototype means composing many modules into a hierarchy — just as a chip integrates multiple IP blocks. SystemC's structural model mirrors RTL: you instantiate submodules as member objects, declare signals as wires, and bind ports to those signals in the parent constructor.

## The Three-Step Pattern

Every structural connection follows the same three steps:

1. **Declare** submodule instances and internal signals as class members.
2. **Construct** submodules (in the initializer list) passing a unique name string.
3. **Bind** ports to signals or other ports in the constructor body.

```cpp
SC_MODULE(Top) {
    // Step 1: declare children and wires
    Cpu    cpu;
    Memory mem;
    sc_signal<sc_uint<32>> addr_bus;
    sc_signal<sc_uint<32>> data_bus;
    sc_signal<bool>        wr_en;
    sc_in<bool>            clk;

    // Step 2: construct children, Step 3: bind ports
    SC_CTOR(Top) : cpu("cpu"), mem("mem") {
        cpu.clk(clk);
        cpu.addr(addr_bus);
        cpu.data(data_bus);
        cpu.wr_en(wr_en);

        mem.clk(clk);
        mem.addr(addr_bus);
        mem.data(data_bus);
        mem.wr_en(wr_en);
    }
};
```

`addr_bus`, `data_bus`, and `wr_en` act as wires. Both `cpu` and `mem` have their ports bound to the same signal objects, creating a shared bus.

## Stack vs. Heap Allocation

Submodules can be allocated on the stack (member objects) or on the heap (pointers). Each has tradeoffs:

| Approach | Declaration | Pros | Cons |
|---|---|---|---|
| Stack (member) | `Cpu cpu;` | No ownership issues, RAII | Cannot be conditionally created |
| Heap (pointer) | `Cpu* cpu;` | Flexible, parameterizable count | Must `new` in constructor; easy to leak |

For a fixed topology, stack allocation is preferred. For parameterized arrays of modules (e.g., N cache banks), use heap allocation with a `std::vector<Module*>`:

```cpp
SC_MODULE(CacheArray) {
    std::vector<CacheBank*> banks;
    std::vector<sc_signal<int>*> sigs;
    int N;

    CacheArray(sc_module_name nm, int n) : sc_module(nm), N(n) {
        for (int i = 0; i < N; ++i) {
            char name[32];
            std::snprintf(name, sizeof(name), "bank_%d", i);
            banks.push_back(new CacheBank(name));
            sigs.push_back(new sc_signal<int>());
            banks[i]->in(*sigs[i]);
        }
    }
};
```

## Port Binding Syntax

SystemC supports two equivalent port-binding syntaxes:

```cpp
// Named binding (operator() — preferred)
cpu.addr(addr_bus);

// Positional-style via sc_port::bind (less common)
cpu.addr.bind(addr_bus);
```

The parenthesis operator is idiomatic and the convention in all major EDA flows.

## Binding Port to Port (Hierarchical Passthrough)

Sometimes a parent module needs to expose a child's port directly through its own interface. You bind a parent port directly to a child port — no intermediate signal is needed:

```cpp
SC_MODULE(Wrapper) {
    sc_in<bool>  ext_clk;   // parent port
    Inner        inner;

    SC_CTOR(Wrapper) : inner("inner") {
        inner.clk(ext_clk);  // parent port -> child port, no signal needed
    }
};
```

The kernel validates that port-to-port binding is directionally consistent at elaboration time.

## Elaboration Checks

After all constructors return, the SystemC kernel performs elaboration checks:

- Every port must be bound to exactly one channel or another port.
- No circular combinational sensitivity is allowed.
- Port types must match the channel type.

Unbound ports cause a fatal elaboration error before simulation starts, which is a valuable early-catch safety net compared to runtime debugging.

## Common Pitfalls

- **Binding after `sc_start()`.** Port binding is illegal once simulation has begun.
- **Using the same signal name string for two different `sc_signal` objects.** Names must be unique within a scope, or the kernel will warn.
- **Forgetting to bind a port.** The error message from the kernel identifies the unbound port by its hierarchical name, making it easy to find.
- **Connecting mismatched types.** `sc_signal<int>` cannot bind to `sc_in<bool>`; the compiler catches this as a template type error.

> **Interview answer:** Submodule instantiation in SystemC follows three steps in the parent constructor: declare children and `sc_signal` wires as members, construct children (with a unique name) in the initializer list, then bind each child port to a signal or parent port using the `port(channel)` syntax. All bindings must be complete before `sc_start()` is called.
