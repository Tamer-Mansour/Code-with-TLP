# Reusable IP Model Libraries

Writing a UART model from scratch for every project is wasteful. Reusable IP model libraries let teams share, version, and reuse verified peripheral models across platforms, dramatically cutting VP build time.

## What Makes an IP Model Reusable?

A reusable model has three properties:

1. **Parameterized interface** — base address, IRQ number, and FIFO depth are constructor arguments, not hard-coded constants.
2. **Clean socket boundary** — exposes only TLM-2.0 target sockets and SystemC signal ports; no project-specific dependencies.
3. **Self-contained** — compiles without knowing anything about the platform it will be plugged into.

```cpp
class UartModel : public sc_core::sc_module {
public:
    tlm_utils::simple_target_socket<UartModel> t_socket;
    sc_core::sc_out<bool> irq;

    SC_HAS_PROCESS(UartModel);
    UartModel(sc_core::sc_module_name name,
              uint32_t fifo_depth = 16,
              uint32_t baud_rate  = 115200)
        : sc_module(name), fifo_depth(fifo_depth), baud_rate(baud_rate) {
        t_socket.register_b_transport(this, &UartModel::b_transport);
    }
private:
    uint32_t fifo_depth, baud_rate;
    void b_transport(tlm::tlm_generic_payload &, sc_core::sc_time &);
};
```

## Industry IP Model Libraries

| Library | Maintained by | Notable models |
|---|---|---|
| OVPsim / Imperas | Imperas | Hundreds of processor ISS + peripheral models |
| Synopsys VDK | Synopsys | ARC, ARM, MIPS processors |
| Arm Fast Models | Arm | Cortex-A/M/R ISS, GIC, PL011 UART |
| QEMU | Open source | Broad board support, exportable as VP components |
| Accellera TLM kit | Community | Reference router, memory, and bus models |

For MCU-class VPs, Arm Fast Models is the most common commercial choice; QEMU is the most common open-source starting point.

## Versioning and Compatibility

IP models must be version-locked to the platform that uses them. Use semantic versioning:

- **Major version** — breaking API change (socket renamed, constructor signature changed).
- **Minor version** — new feature, backward compatible (new optional constructor argument).
- **Patch** — bug fix, no API change.

```cmake
find_package(TlpIpLib 2.4.0 REQUIRED)
target_link_libraries(myplatform TlpIpLib::uart TlpIpLib::timer TlpIpLib::gpio)
```

Lock the version in `CMakeLists.txt` so CI always uses the same model even when the library is updated.

## Model Quality Tiers

Not all library models are equally faithful:

| Tier | Description | Use case |
|---|---|---|
| **Stub** | Returns reset values, accepts writes without effect | Compile firmware without hardware |
| **Behavioral** | Correct functional behavior, no timing | Driver development |
| **Timed** | Annotated latencies on transactions | Performance estimation |
| **Cycle-accurate** | Matches RTL cycle-by-cycle | Hardware/software co-verification |

Request the tier that matches your project's fidelity requirement — higher tiers are slower and cost more.

## Building an In-House Library

When commercial models are unavailable, build an in-house library:

```
ip-models/
├── CMakeLists.txt
├── include/
│   ├── uart_model.h
│   ├── timer_model.h
│   └── gpio_model.h
├── src/
│   ├── uart_model.cpp
│   ├── timer_model.cpp
│   └── gpio_model.cpp
└── tests/
    ├── uart_selftest.cpp   ← standalone SystemC testbench per model
    └── timer_selftest.cpp
```

Each model has its own unit-level testbench. This lets you verify a model independently before plugging it into a platform.

## Register Model Auto-Generation

Large peripheral register files can be auto-generated from IP-XACT or SVD (System View Description) files — both are XML formats widely used in the embedded industry:

```bash
# Generate register model from SVD file
python svd2tlm.py stm32f4xx.svd --output ip-models/src/
```

Auto-generation eliminates transcription errors and keeps register names in sync with vendor documentation.

**Interview answer:** A reusable IP model exposes only TLM-2.0 sockets and sc_signal ports, takes all platform-specific values (base address, IRQ number) as constructor arguments, and is versioned independently. The most widely used commercial libraries are Arm Fast Models and Imperas OVPsim; open-source teams often extract peripheral models from QEMU.
