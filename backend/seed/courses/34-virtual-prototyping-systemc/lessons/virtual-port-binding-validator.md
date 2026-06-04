# Module Hierarchy Port Binding Validator

Port binding is one of the most structurally important constraints in SystemC. The IEEE 1666 standard requires that every port in a design is bound exactly once during elaboration. Unbound ports and doubly-bound ports are both fatal errors that prevent simulation from starting.

## Why Port Binding Is Strictly Validated

Unlike VHDL or Verilog, where unconnected ports may be implicitly tied off, SystemC treats an unbound port as a hard error. The reason is the class library model: a port is implemented as a pointer to an interface. If that pointer is null (unbound), any attempt to call through it at simulation time causes a null pointer dereference. The elaboration-time check prevents this class of crash entirely.

```
ERROR: (E109) complete binding failed: port not bound: cpu.clk_port
```

This message appears before `sc_start()` if any port remains unbound.

## Three Classes of Binding Error

**UNBOUND_PORT**: A port was declared in the module's interface but no binding statement connected it to a signal or parent port.

```cpp
SC_MODULE(Cpu) {
    sc_in<bool> clk;    // declared
    sc_in<bool> reset;  // declared — but never bound in sc_main → UNBOUND
    SC_CTOR(Cpu) {}
};
```

**DOUBLE_BOUND**: A port was bound more than once. Because `sc_port` holds a single interface pointer, a second binding overwrites the first, which is almost always a mistake.

```cpp
cpu.clk(sysclk);   // first binding
cpu.clk(sysclk);   // second binding → DOUBLE_BOUND error
```

**UNDECLARED_PORT**: A binding statement references a port name that does not exist in the module's port list. This happens most often when a port is renamed in the header but the sc_main binding code is not updated.

## Elaboration Phase Enforcement

All port bindings must be complete before `sc_start()` is called. The elaboration phase consists of:

1. Module constructors run (ports are declared, submodules are instantiated)
2. `before_end_of_elaboration()` callbacks run
3. Port binding completeness is checked
4. `end_of_elaboration()` callbacks run
5. `start_of_simulation()` callbacks run
6. `sc_start()` begins simulation

If the binding check at step 3 finds any error, `sc_report_handler` is called with severity `SC_ERROR` and simulation terminates.

## Pass-Through Bindings

In a hierarchy, a parent module may expose child ports at its own interface. This is called a pass-through binding:

```cpp
SC_MODULE(SoC) {
    sc_in<bool> clk;          // SoC's own port

    Cpu   cpu_inst;
    Uart  uart_inst;

    SC_CTOR(SoC) : cpu_inst("cpu"), uart_inst("uart") {
        cpu_inst.clk(clk);    // pass-through: SoC.clk → cpu.clk
        uart_inst.clk(clk);   // same signal, two bindings to different ports
    }
};
```

Pass-through bindings are valid — the same `sc_signal` can be bound to multiple ports as long as each individual port is bound exactly once.

## Tools for Diagnosis

When a simulation aborts at elaboration, the error message includes the full hierarchical path to the unbound port (e.g., `top.soc.cpu.clk`). Use this path to locate the missing binding in your sc_main or parent module constructor.

## Reference

For the normative elaboration rules:

- **IEEE Std. 1666-2023** (free via Accellera at https://www.accellera.org/downloads/standards/systemc): Sections 5.15 (sc_port binding) and 4.4 (elaboration phase callbacks)
- **SystemC and TLM-2.0 Introductory Tutorial** (Doulos, free PDF at https://www.doulos.com/media/1408/systemc_tutorial.pdf): Chapter on module hierarchy and port connections

> **Interview answer:** SystemC requires every port to be bound exactly once before sc_start(). Unbound ports are caught at elaboration time with an SC_ERROR because an unbound port is a null interface pointer that would crash at simulation time. Doubly-bound ports are also errors. The elaboration check runs after all module constructors complete.
