# Structural vs Behavioral Description

SystemC supports two complementary modeling styles within the same language: *structural* description, which specifies how components are connected, and *behavioral* description, which specifies what a component computes. Mixing them appropriately — at the right abstraction level — is the core skill of virtual prototype design.

## Definitions

**Structural description** expresses the netlist: which modules exist, how their ports are wired together through signals or TLM sockets, and which module instantiates which. The parent module's constructor is the structural description.

**Behavioral description** expresses the computation: what happens over time inside a module — how inputs map to outputs, how state evolves, what transactions are performed. Processes (`SC_METHOD`, `SC_THREAD`) contain the behavioral description.

## Side-by-Side Comparison

```cpp
// --- STRUCTURAL (the Top module constructor) ---
SC_CTOR(Top) : cpu("cpu"), bus("bus"), mem("mem") {
    cpu.clk(clk);
    cpu.data_socket(bus.target_socket);  // TLM binding
    bus.initiator_socket(mem.target);
}

// --- BEHAVIORAL (inside a module's process) ---
void Cpu::run() {
    while (true) {
        wait(clk.posedge_event());
        if (fetch_addr != 0) {
            tlm::tlm_generic_payload trans;
            trans.set_address(fetch_addr);
            trans.set_read();
            data_socket->b_transport(trans, delay);
            execute(trans.get_data_ptr());
        }
    }
}
```

The structural code describes *topology*; the behavioral code describes *protocol and algorithm*.

## Abstraction Levels and Their Style

| Level | Structural Granularity | Behavioral Description |
|---|---|---|
| RTL | Gates and flip-flops | Clock-cycle-accurate `SC_CTHREAD` |
| Cycle-accurate TLM | IP blocks with TLM sockets | Cycle-counted `SC_THREAD` |
| Transaction-level (TLM-2.0) | Initiators, targets, interconnect | Timed `b_transport` calls |
| Untimed / functional | Functional blocks | Pure C++ functions, no `wait()` |

As abstraction rises, behavioral complexity increases and structural detail decreases. A TLM model replaces individual signal wires with a single TLM socket, but the behavioral model inside the initiator becomes more complex (protocol handling).

## The Separation Principle

Good SystemC design keeps structural and behavioral concerns in separate code regions:

- The **constructor** is exclusively structural: instantiate children, bind ports, register processes.
- **Processes** are exclusively behavioral: read inputs, compute, write outputs, advance time.

Violating this — for example, driving a signal in the constructor — produces waveform glitches or race conditions because the signal update happens before the delta-cycle scheduling mechanism is active.

## Mixed Example: A Pipeline Stage

```cpp
SC_MODULE(PipeStage) {
    // Structural members
    sc_in<int>    in_val;
    sc_out<int>   out_val;
    sc_in<bool>   clk;

    // Behavioral state
    int latched;

    SC_CTOR(PipeStage) : latched(0) {
        // Structural: register the behavioral process
        SC_CTHREAD(latch, clk.pos());
    }

    // Behavioral: runs every rising clock edge
    void latch() {
        while (true) {
            latched = in_val.read();
            wait();
            out_val.write(latched);
        }
    }
};
```

The constructor is structural (declares the process). `latch()` is behavioral (reads, stores, writes).

## When to Use SC_METHOD vs SC_THREAD

- **SC_METHOD**: Pure combinational logic, no memory between calls, no `wait()`. Fast and event-driven.
- **SC_THREAD**: Sequential protocol, multi-phase handshake, or any code that needs to suspend with `wait()`. Slower but expressive.
- **SC_CTHREAD**: RTL-style flip-flop behavior clocked on a specific clock edge.

## Common Pitfalls

- **Writing simulation logic (wait, signal drive) in the constructor.** This is structural code space; behavioral code belongs in processes.
- **Using `SC_METHOD` with `wait()`.** `SC_METHOD` processes have no stack context; calling `wait()` inside one causes a runtime error.
- **Exposing internal signals as ports.** Keep structural and behavioral boundaries clean; child modules should communicate through their declared ports, not by directly accessing parent signals.

> **Interview answer:** Structural description defines the module hierarchy and how ports/sockets are connected — it lives in the constructor. Behavioral description defines what a module computes over time — it lives in processes (`SC_METHOD`, `SC_THREAD`). Keeping them cleanly separated makes the model easier to verify, synthesize, or replace at a different abstraction level.
