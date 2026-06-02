# SystemC and Transaction-Level Modeling

**SystemC** is a C++ class library and simulation kernel standardised as IEEE 1666. It lets hardware engineers describe digital systems in C++ and simulate them at multiple levels of abstraction. **Transaction-Level Modeling (TLM)** is the dominant style: instead of toggling individual signals, components communicate by calling functions that represent complete transactions (a read, a write, a burst).

## Why SystemC TLM?

The traditional hardware design path — RTL in Verilog/VHDL → simulation → synthesis — is too slow for early software development. A SystemC TLM model of the same SoC can run 100x-1000x faster than RTL simulation while still being accurate enough to boot a real operating system and run meaningful workloads.

Key benefits:

- Write platform models in standard C++ — reuse the entire C++ ecosystem.
- Mix abstraction levels: a cycle-accurate CPU next to a loosely-timed memory subsystem.
- Generate RTL from a SystemC model using commercial HLS (High-Level Synthesis) tools.
- Industry-standard API means models can be exchanged between tools (Synopsys VDK, Cadence Virtual System Platform, Mentor Vista).

## TLM-2.0 Core Concepts

The TLM-2.0 standard (part of SystemC 2.3+) defines a portable API built around three abstractions:

### 1. Generic Payload (`tlm_generic_payload`)

A struct that carries one memory-mapped transaction:

```cpp
tlm::tlm_generic_payload trans;
trans.set_command(tlm::TLM_WRITE_COMMAND);
trans.set_address(0x10000000);
trans.set_data_ptr(reinterpret_cast<unsigned char*>(&data));
trans.set_data_length(4);
trans.set_streaming_width(4);
trans.set_byte_enable_ptr(nullptr);
trans.set_dmi_allowed(false);
trans.set_response_status(tlm::TLM_INCOMPLETE_RESPONSE);
```

### 2. Sockets (`tlm_initiator_socket` / `tlm_target_socket`)

Typed ports that connect initiators (masters) to targets (slaves). Binding replaces wire connections:

```cpp
// In the CPU model
tlm_utils::simple_initiator_socket<CPU> ibus;
// In the memory model
tlm_utils::simple_target_socket<Memory> mem_socket;
// Binding (in sc_main)
cpu.ibus.bind(mem.mem_socket);
```

### 3. Blocking vs. Non-Blocking Transport

**Blocking** (`b_transport`): the call returns only when the transaction completes. Simple to write, used in Loosely-Timed (LT) models.

```cpp
void CPU::do_read(uint64_t addr, uint32_t &val) {
    tlm::tlm_generic_payload trans;
    sc_core::sc_time delay = sc_core::SC_ZERO_TIME;
    // ... fill trans fields ...
    ibus->b_transport(trans, delay);
}
```

**Non-blocking** (`nb_transport_fw` / `nb_transport_bw`): the call returns immediately; timing is communicated via time annotations. Used in Approximately-Timed (AT) models for bus protocol accuracy.

## Loosely-Timed vs. Approximately-Timed

| Style | Transport | Timing | Speed |
|---|---|---|---|
| Loosely-Timed (LT) | `b_transport` | Annotated delay added after call | Fastest, ~OS boot speed |
| Approximately-Timed (AT) | `nb_transport` | Explicit phases (BEGIN_REQ, END_REQ, …) | Slower, models bus contention |

For early software bring-up, LT is almost always used. AT is introduced when bus-level timing (arbitration, pipelining) matters.

## Direct Memory Interface (DMI)

Copying data through the generic payload interface on every access is expensive. TLM-2.0 DMI lets a target grant direct pointer access to its memory:

```cpp
// Memory grants DMI hint
if (trans.is_dmi_allowed()) {
    tlm::tlm_dmi dmi_data;
    if (mem_socket->get_direct_mem_ptr(trans, dmi_data)) {
        dmi_ptr = dmi_data.get_dmi_ptr();  // Host pointer to guest memory
    }
}
```

Once DMI is granted, the initiator reads/writes directly via the host pointer — simulating a DMA-style bulk transfer at native C++ speed.

## Worked Example: Memory-Mapped Register Read

```cpp
// UART target: respond to status register read
void UART::b_transport(tlm::tlm_generic_payload& trans, sc_core::sc_time& delay) {
    uint64_t addr   = trans.get_address();
    uint8_t* ptr    = trans.get_data_ptr();
    unsigned int len = trans.get_data_length();

    if (trans.get_command() == tlm::TLM_READ_COMMAND) {
        if (addr == UART_STATUS_REG) {
            uint32_t status = tx_ready ? 0x1 : 0x0;
            memcpy(ptr, &status, len);
            delay += sc_core::sc_time(10, sc_core::SC_NS);  // Annotated delay
        }
    }
    trans.set_response_status(tlm::TLM_OK_RESPONSE);
}
```

The annotated delay tells the kernel to advance simulation time without actually stalling the calling process — this is what makes LT models fast.

## Common Pitfall

Forgetting to set `response_status` to `TLM_OK_RESPONSE` causes silent assertion failures or undefined behaviour in downstream initiators. Always set it before returning from `b_transport`.

## Interview Answer

> "SystemC TLM-2.0 allows hardware platforms to be modelled in C++ using function-call transactions instead of signal toggling. Loosely-timed models using `b_transport` run at OS-boot speeds and are used for early software bring-up; approximately-timed models add bus-protocol accuracy at lower simulation speed."
