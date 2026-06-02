# Composition Patterns for Platforms

A virtual prototype of a complete SoC is not a single monolithic module — it is composed from many IP blocks assembled into subsystems, and subsystems assembled into a platform. Knowing the recurring composition patterns saves time and prevents structural mistakes that are hard to refactor later.

## Pattern 1: Flat Platform Wrapper

All IP blocks are direct children of a single `Top` module. Best for small designs or early-stage integration where the hierarchy is not yet known.

```cpp
SC_MODULE(Top) {
    Cpu     cpu;
    Memory  mem;
    Uart    uart;
    Bus     bus;

    SC_CTOR(Top) : cpu("cpu"), mem("mem"), uart("uart"), bus("bus") {
        cpu.socket(bus.target);
        bus.mem_socket(mem.target);
        bus.uart_socket(uart.target);
    }
};
```

Advantage: simple. Disadvantage: the constructor becomes unwieldy as IP count grows; reuse is hard.

## Pattern 2: Subsystem Hierarchy

Group related IPs into subsystem modules. The platform instantiates subsystems:

```cpp
SC_MODULE(CpuSubsystem) {
    Cpu   core0, core1;
    L1Cache cache;
    sc_in<bool> clk;
    tlm_utils::simple_initiator_socket<CpuSubsystem> mem_socket;

    SC_CTOR(CpuSubsystem) : core0("core0"), core1("core1"), cache("cache") {
        core0.cache_socket(cache.cpu0_target);
        core1.cache_socket(cache.cpu1_target);
        cache.mem_socket(mem_socket);  // passthrough to platform
    }
};

SC_MODULE(Platform) {
    CpuSubsystem cpu_ss;
    Memory       ddr;
    // ...
    SC_CTOR(Platform) : cpu_ss("cpu_ss"), ddr("ddr") {
        cpu_ss.mem_socket(ddr.target);
    }
};
```

Advantage: each subsystem can be unit-tested independently. Subsystem modules are reusable across platform variants.

## Pattern 3: Parameterized Arrays

When a platform contains N identical instances (cache ways, DMA channels, processing elements):

```cpp
SC_MODULE(MultiCorePlatform) {
    std::vector<Core*>             cores;
    std::vector<sc_signal<bool>*>  irq_lines;
    InterruptController            intc;
    int N;

    MultiCorePlatform(sc_module_name nm, int n)
        : sc_module(nm), intc("intc"), N(n)
    {
        for (int i = 0; i < N; ++i) {
            char buf[32];
            std::snprintf(buf, sizeof(buf), "core_%d", i);
            cores.push_back(new Core(buf));
            irq_lines.push_back(new sc_signal<bool>());
            intc.irq_out[i](*irq_lines[i]);
            cores[i]->irq(*irq_lines[i]);
        }
    }
};
```

Use `std::vector` + raw pointers (or `unique_ptr`) for dynamic instantiation. Always generate unique names.

## Pattern 4: Configurable Variants via Template Parameters

When a module must work with different data widths or protocol variants:

```cpp
template<unsigned WIDTH>
SC_MODULE(GenericFifo) {
    sc_in<sc_uint<WIDTH>>  din;
    sc_out<sc_uint<WIDTH>> dout;
    sc_out<bool>           empty, full;
    // ...
    SC_CTOR(GenericFifo) { SC_THREAD(run); }
    void run();
};

// Instantiation
GenericFifo<32> data_fifo("data_fifo");
GenericFifo<8>  cmd_fifo("cmd_fifo");
```

Template parameters are resolved at compile time — no runtime overhead.

## Pattern 5: Adapter / Bridge Module

When two IP blocks use different protocols, insert an adapter:

```cpp
SC_MODULE(AhbToApbBridge) {
    // AHB target side
    tlm_utils::simple_target_socket<AhbToApbBridge> ahb_target;
    // APB initiator side
    tlm_utils::simple_initiator_socket<AhbToApbBridge> apb_initiator;

    SC_CTOR(AhbToApbBridge) {
        ahb_target.register_b_transport(this, &AhbToApbBridge::b_transport);
    }

    void b_transport(tlm::tlm_generic_payload& trans, sc_time& delay);
};
```

Adapters keep IP blocks protocol-agnostic and easily swappable.

## Pattern 6: Abstract Base + Multiple Implementations

Define an abstract module base for an IP that has multiple fidelity levels:

```cpp
SC_MODULE(MemoryBase) {
    tlm_utils::simple_target_socket<MemoryBase> target;
    virtual void b_transport(tlm::tlm_generic_payload&, sc_time&) = 0;
    SC_CTOR(MemoryBase) {
        target.register_b_transport(this, &MemoryBase::b_transport);
    }
};

struct FastRam   : MemoryBase { /* zero-delay model */ ... };
struct TimedDram : MemoryBase { /* cycle-accurate model */ ... };
```

The platform constructor accepts a `MemoryBase*` pointer, so the fidelity level can be selected at runtime.

## Choosing the Right Pattern

| Situation | Recommended Pattern |
|---|---|
| Small design, < 10 IPs | Flat wrapper |
| Reusable subsystem clusters | Subsystem hierarchy |
| N identical instances | Parameterized array |
| Multiple data widths | Template parameters |
| Protocol mismatch between IPs | Adapter/bridge |
| Multiple model fidelity levels | Abstract base |

> **Interview answer:** Platform composition in SystemC follows well-established patterns: subsystem hierarchies for reuse and unit testing, parameterized arrays for N-way replicated blocks, template parameters for compile-time width variation, and adapter modules for protocol bridging. The key principle is that each module should have a single responsibility and a minimal, stable interface so it can be swapped or retargeted independently.
