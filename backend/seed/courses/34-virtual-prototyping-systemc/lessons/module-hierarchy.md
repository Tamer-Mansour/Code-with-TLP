# Building a Module Hierarchy

Real hardware is hierarchical: a SoC contains subsystems, subsystems contain IPs, IPs contain submodules. SystemC mirrors this directly. Understanding how to build, name, and navigate module hierarchies is essential for creating maintainable, scalable models.

## Modules as Building Blocks

Every `SC_MODULE` is a C++ class that can:
- Contain other module instances as member variables.
- Declare ports (`sc_in`, `sc_out`, `sc_inout`) for external connectivity.
- Declare internal signals (`sc_signal`) to connect sub-modules.

```cpp
SC_MODULE(Alu) {
    sc_in<sc_uint<32>>  a, b;
    sc_in<sc_uint<4>>   op;
    sc_out<sc_uint<32>> result;

    SC_CTOR(Alu) {
        SC_METHOD(compute);
        sensitive << a << b << op;
    }
    void compute();
};
```

## Composing a Hierarchy

A parent module declares child modules as **member objects** (not pointers, preferably) and binds their ports to local signals or its own ports:

```cpp
SC_MODULE(Datapath) {
    // External ports
    sc_in<sc_uint<32>>  in_a, in_b;
    sc_in<sc_uint<4>>   alu_op;
    sc_out<sc_uint<32>> out;

    // Internal sub-modules
    Alu        alu;
    RegisterFile rf;

    // Internal signals connecting sub-modules
    sc_signal<sc_uint<32>> rf_a_out, rf_b_out;

    SC_CTOR(Datapath)
    : alu("alu"), rf("rf")   // each sub-module gets a name string
    {
        // Bind ALU ports
        alu.a(rf_a_out);      // internal signal
        alu.b(rf_b_out);
        alu.op(alu_op);       // parent's port passed through
        alu.result(out);

        // Bind register file ports
        rf.read_a(rf_a_out);
        rf.read_b(rf_b_out);
    }
};
```

## Naming Conventions

Every module instance must have a unique **hierarchical name**. SystemC builds this name by concatenating parent and child names with dots:

```
Top
 ├── cpu        (Top.cpu)
 │    ├── alu   (Top.cpu.alu)
 │    └── rf    (Top.cpu.rf)
 └── mem        (Top.mem)
```

You query a module's full hierarchical name with:

```cpp
std::cout << alu.name();   // prints "Top.cpu.alu"
```

This name appears in waveform dumps and error reports — choose descriptive, lowercase-with-underscores names.

## Dynamic Instantiation with sc_vector

When you need N identical sub-modules, use `sc_vector` (introduced in IEEE 1666-2011):

```cpp
#include <sysc/utils/sc_vector.h>

SC_MODULE(BankOf8Alus) {
    sc_vector<Alu> alus;

    sc_vector<sc_signal<sc_uint<32>>> results;

    SC_CTOR(BankOf8Alus)
    : alus("alu", 8),       // creates alu[0]..alu[7]
      results("res", 8)
    {
        for (int i = 0; i < 8; ++i) {
            alus[i].result(results[i]);
            // bind remaining ports ...
        }
    }
};
```

Avoid using `new` to heap-allocate modules — it works but loses the automatic name-building hierarchy.

## Port Pass-Through

A parent port can be directly connected to a child port without an intermediate signal:

```cpp
SC_CTOR(Wrapper) {
    child.clk(clk);    // parent's sc_in<bool> clk passed to child's port
    // No sc_signal<bool> needed — same port object is reused
}
```

## Worked Example: Two-Level Hierarchy

```cpp
SC_MODULE(Core) {
    sc_in<bool>        clk, reset;
    sc_out<sc_uint<32>> pc;

    Alu         alu;
    Datapath    dp;
    sc_signal<sc_uint<32>> dp_result;

    SC_CTOR(Core)
    : alu("alu"), dp("dp")
    {
        dp.clk(clk);
        dp.reset(reset);
        dp.result(dp_result);
        alu.a(dp_result);
        // ...
    }
};

int sc_main(int argc, char* argv[]) {
    sc_clock clk("clk", 10, SC_NS);
    sc_signal<bool>        rst;
    sc_signal<sc_uint<32>> pc_out;

    Core core("core");
    core.clk(clk);
    core.reset(rst);
    core.pc(pc_out);

    rst.write(true);
    sc_start(20, SC_NS);
    rst.write(false);
    sc_start(1000, SC_NS);

    return 0;
}
```

## Common Pitfalls

- **Not passing a name string to sub-module constructors** — the `SC_MODULE_NAME` macro can help, but explicit strings are clearer.
- **Binding signals after `sc_start()`** — illegal; all bindings must occur during elaboration.
- **Leaving ports unbound** — the kernel reports an error at simulation start. Every port must be connected to exactly one signal.
- **Using `new` for sub-modules without storing the pointer** — memory leak and loss of hierarchical naming.

> **Interview answer:** "Module hierarchy in SystemC is built by declaring child `SC_MODULE` instances as member variables of a parent module, then binding their ports to local `sc_signal` objects or to the parent's own ports in the constructor. `sc_vector` handles arrays of identical modules. The kernel builds dot-separated hierarchical names automatically."
