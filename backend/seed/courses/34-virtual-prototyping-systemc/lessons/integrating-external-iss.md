# Integrating an External ISS (e.g. QEMU)

Building a CPU model from scratch is expensive. For standard ISAs (RISC-V, Arm, x86, MIPS) an open-source ISS already exists and has been validated against real hardware running real operating systems. The practical approach for most virtual prototypes is to **integrate an existing ISS** — most commonly QEMU — with a SystemC TLM-2.0 platform rather than reimplementing the CPU. This section explains how that integration works.

## Why Use an External ISS?

- **QEMU** supports 50+ architectures, boots Linux and bare-metal firmware, runs at 200–1000 MIPS.
- **Spike** is the RISC-V ISA reference simulator — deterministic, easy to instrument.
- **OVPsim** and **Imperas** provide commercial ISS models for ARM Cortex-M/A, RISC-V, and MIPS with TLM wrappers included.

Rolling your own ISS for a standard ISA is almost never the right answer unless you are adding a proprietary ISA extension.

## Integration Architecture

The external ISS runs as a separate thread (or process) alongside SystemC. The key integration points are:

```
┌─────────────────────────────────────┐
│          SystemC Platform           │
│  ┌───────────────┐  ┌────────────┐  │
│  │  ISS Wrapper  │  │  Bus/Mem   │  │
│  │  (SC_MODULE)  │──│  Peripherals│  │
│  └──────┬────────┘  └────────────┘  │
│         │ TLM initiator socket       │
└─────────┼───────────────────────────┘
          │  callbacks / shared memory
┌─────────┴───────────────────────────┐
│         External ISS (QEMU/Spike)   │
│  fetch/decode/execute loop          │
│  memory callbacks → TLM b_transport │
└─────────────────────────────────────┘
```

The wrapper SC_MODULE owns the TLM initiator socket and exposes two C function callbacks to the ISS:
- `on_read(addr, size)` → calls `b_transport` and returns the data
- `on_write(addr, size, data)` → calls `b_transport` to write

## QEMU as a Library: `libqemu`

QEMU provides a library mode (`--enable-libqemu-build`) in some downstream forks (e.g., from Linaro, Xilinx, or academic projects). The ISS wrapper creates a QEMU instance, registers memory callbacks, then calls `qemu_run()` in a SystemC thread:

```cpp
SC_MODULE(QEMUWrapper) {
    tlm_utils::simple_initiator_socket<QEMUWrapper> bus;

    SC_CTOR(QEMUWrapper) {
        SC_THREAD(run);
    }

    void run() {
        qemu_init(target_arch, kernel_image);
        qemu_register_read_cb(qemu_read_cb, this);
        qemu_register_write_cb(qemu_write_cb, this);
        qemu_run(); // runs until QEMU exits
    }

    static uint64_t qemu_read_cb(void* opaque, uint64_t addr, int size) {
        auto* self = static_cast<QEMUWrapper*>(opaque);
        return self->do_tlm_read(addr, size);
    }

    uint64_t do_tlm_read(uint64_t addr, int size) {
        tlm::tlm_generic_payload trans;
        uint64_t data = 0;
        trans.set_command(tlm::TLM_READ_COMMAND);
        trans.set_address(addr);
        trans.set_data_ptr(reinterpret_cast<uint8_t*>(&data));
        trans.set_data_length(size);
        trans.set_streaming_width(size);
        sc_core::sc_time delay = SC_ZERO_TIME;
        bus->b_transport(trans, delay);
        return data;
    }
};
```

## Spike Integration (RISC-V)

Spike exposes a cleaner C++ API. The `sim_t` class can be configured with a custom memory map and an optional `fesvr` (Front-End Server) for semihosting. The ISS wrapper creates a `sim_t`, maps SystemC memory regions into it, then steps the ISS manually:

```cpp
void SpikeWrapper::run() {
    processor_t* proc = sim->get_core(0);

    while (running) {
        proc->step(quantum_instructions); // run N instructions
        wait(quantum_time);               // yield to SystemC
    }
}
```

Each call to `proc->step()` triggers RISC-V fetch-execute for the given instruction count. Memory accesses call back into the custom memory interface, which the wrapper forwards to `b_transport`.

## Interrupt Delivery

Interrupts arrive as SystemC signals. The wrapper converts them to ISS interrupt assertions:

```cpp
// Called when an interrupt line changes
void QEMUWrapper::irq_changed(bool level) {
    if (level) {
        qemu_set_irq(cpu_irq, 1); // assert
    } else {
        qemu_set_irq(cpu_irq, 0); // deassert
    }
}
```

The ISS checks pending interrupts at the next quantum boundary and takes the trap via its internal exception machinery.

## Temporal Decoupling Across the Boundary

The ISS runs ahead of SystemC time by one quantum. The wrapper accumulates a `local_time` offset and synchronizes with `wait()` at quantum boundaries. Memory callbacks must add the accumulated offset to the `delay` parameter of each `b_transport` call so that the interconnect sees a consistent time ordering.

## Practical Integration Checklist

- **Endianness**: QEMU and the SystemC platform must agree on byte order for multi-byte transactions.
- **Address space**: Map the same regions in both the ISS memory map and the TLM address map.
- **Reset vector**: The ISS must start at the same reset vector as your real SoC.
- **Semihosting**: Decide early whether the ISS uses semihosting calls (e.g., `BKPT 0xAB` in Arm) for stdout and file I/O.
- **GDB stub**: Most external ISS tools provide a built-in GDB remote serial protocol stub — connect your IDE and set breakpoints in the virtual prototype exactly as you would on hardware.

## Common Pitfalls

- **Thread safety**: QEMU's internal state is not thread-safe. All QEMU API calls must come from the SystemC thread that owns the wrapper.
- **Blocking callbacks**: If a `b_transport` call blocks for many microseconds of simulated time, the QEMU thread stalls for the same duration. Keep bus latencies small or use non-blocking peripheral models.
- **Version pinning**: QEMU's internal API changes with every major version. Pin to a specific QEMU fork and test before upgrading.

## Interview Answer

> "To integrate QEMU into a SystemC platform, you write an SC_MODULE wrapper that owns the TLM initiator socket and registers read/write callbacks with QEMU. QEMU calls those callbacks on every memory access; the callback performs a `b_transport` to the SystemC interconnect. Interrupts are delivered by calling QEMU's IRQ API from SystemC signal sensitivity. Temporal decoupling is maintained by running QEMU for one quantum's worth of instructions before calling `wait()` to yield to the SystemC scheduler."
