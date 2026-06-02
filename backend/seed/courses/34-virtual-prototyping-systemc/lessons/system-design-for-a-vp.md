# System Design: Architect a VP in an Interview

System design questions for VP/embedded roles ask you to sketch a complete VP from scratch in 30–45 minutes. This lesson walks through a structured methodology and a worked example so you can answer confidently.

## The Framework: Five Steps in Order

1. **Clarify requirements** — what SW must run? what timing accuracy is needed? what is the schedule?
2. **Identify the components** — CPU, memory, interconnect, peripherals
3. **Choose abstraction levels** — functional, AT-TLM, or cycle-accurate per component
4. **Define the interfaces** — TLM sockets, `sc_signal` lines, shared memory
5. **Describe the boot and test flow** — how does SW load and what does "done" look like?

Never jump to code before completing steps 1–3. Interviewers reward structured thinking.

## Worked Example: Architect a VP for a RISC-V IoT SoC

**The prompt:** "Design a VP for a RISC-V SoC with a Cortex-M0-equivalent core, 256 KB SRAM, a UART, a SPI master, and a DMA controller. The goal is to boot FreeRTOS and run a sensor data pipeline."

### Step 1: Clarify Requirements

- Do we need cycle-accurate CPU? (No — functional ISS is sufficient for FreeRTOS bring-up)
- What is the timing accuracy requirement? (±30 % acceptable for this phase)
- Will the DMA model need interrupt completion? (Yes — FreeRTOS driver uses DMA completion ISR)
- Host platform? (Linux x86 workstation, single-threaded SystemC)

### Step 2: Identify Components

| Component | Model type | Rationale |
|-----------|-----------|-----------|
| RISC-V CPU | Functional ISS (e.g., QEMU-wrapped) | Speed, no perf. analysis needed |
| SRAM (256 KB) | TLM target memory | Flat array, DMI enabled |
| Interconnect | TLM router | Decode address, forward transaction |
| UART | TLM peripheral + `sc_signal<bool>` IRQ | Register model + interrupt |
| SPI master | TLM peripheral | Register model, no signal-level |
| DMA controller | TLM initiator + target | Reads from src, writes to dst, fires IRQ |
| Boot ROM | TLM target, read-only | Contains reset vector and startup code |

### Step 3: Choose Abstraction Levels

```
CPU (ISS) ──b_transport──► Router ──b_transport──► SRAM
                                 └──b_transport──► UART
                                 └──b_transport──► SPI
                                 └──b_transport──► DMA (target side)

DMA (initiator) ──b_transport──► Router ──► SRAM

UART.irq ──sc_signal<bool>──► CPU IRQ port
DMA.irq  ──sc_signal<bool>──► CPU IRQ port
```

All links use AT-TLM `b_transport`. Temporal decoupling quantum: 1 µs (good balance for FreeRTOS tick = 1 ms).

### Step 4: Define Interfaces

```cpp
// DMA Controller: dual-role (target for config, initiator for transfers)
SC_MODULE(DmaController) {
    tlm_utils::simple_target_socket<DmaController>    cfg_socket;   // CPU config
    tlm_utils::simple_initiator_socket<DmaController> mem_socket;   // DMA transfers
    sc_core::sc_out<bool>                             irq;          // completion

    uint32_t src_addr, dst_addr, length, control;

    void b_transport(tlm::tlm_generic_payload& gp, sc_core::sc_time& delay);
    void dma_thread();   // SC_THREAD — runs transfer when triggered

    SC_CTOR(DmaController) {
        cfg_socket.register_b_transport(this, &DmaController::b_transport);
        SC_THREAD(dma_thread);
    }
};
```

### Step 5: Boot and Test Flow

```
1. Reset vector → Boot ROM → copies image to SRAM → jumps to FreeRTOS entry
2. FreeRTOS scheduler starts, creates sensor_task and uart_task
3. sensor_task reads SPI register → DMA kicks off transfer → DMA fires IRQ
4. uart_task receives data via FreeRTOS queue → writes to UART TX register
5. UART model posts byte to a host file / stdout for inspection
```

A passing test: FreeRTOS boots, sensor_task runs 10 iterations, and uart_task outputs 10 lines to the host console — all within 2 seconds of wall-clock simulation time.

## Common Interview Mistakes to Avoid

- **Forgetting interrupt lines** — the most commonly missed connection. Interviewers specifically look for `sc_signal<bool>` IRQ wires.
- **Making everything cycle-accurate** — shows you misunderstand the trade-off. Say explicitly why functional ISS is chosen here.
- **No DMI on SRAM** — for a flat memory used by DMA, DMI is a standard optimization that shows expertise.
- **No temporal decoupling** — omitting this makes the VP orders of magnitude slower than it needs to be.
- **Not describing the test** — interviewers want to know what "success" looks like.

## How to Present the Architecture on a Whiteboard

```
┌─────────────────────────────────────────────────┐
│                  SystemC Platform                │
│                                                  │
│  ┌──────────┐   b_transport   ┌──────────────┐  │
│  │ RISC-V   ├────────────────►│    Router    │  │
│  │  ISS     │                 │  (TLM-2.0)   │  │
│  └────┬─────┘                 └──┬───┬───┬───┘  │
│       │ irq[0..1]                │   │   │      │
│       │ sc_signal<bool>          ▼   ▼   ▼      │
│  ┌────┴───────────────────────────────────────┐  │
│  │        SRAM  │  UART  │  SPI  │  DMA       │  │
│  └────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

Draw this, label the sockets, then walk through the data flow for one use case (e.g., DMA transfer). This demonstrates system-level thinking — exactly what senior SoC roles require.

## Interview Answer (Meta)

> "I approach VP design in five steps: clarify what SW must run and what timing accuracy is acceptable, identify all hardware components, choose the appropriate abstraction level for each (functional ISS for CPU, AT-TLM for peripherals), define TLM socket and interrupt signal connections, and describe the boot and test flow. For a FreeRTOS IoT SoC the right choice is almost always: functional ISS for the CPU, AT-TLM for all peripherals, `sc_signal<bool>` interrupt wires, and DMI-enabled SRAM — giving fast simulation with enough fidelity for driver and OS validation."
