# Real Protocols: AMBA AXI, AHB, APB

ARM's AMBA family defines three bus protocols that cover the full performance spectrum of an SoC. Understanding their key differences lets you pick the right abstraction for each part of your virtual prototype.

## The AMBA Hierarchy at a Glance

```
High Performance   ←─────────────────────────────→   Low Power / Area
  ┌────────────┐        ┌──────────┐        ┌──────────┐
  │  AXI / ACE │        │   AHB    │        │   APB    │
  │ Pipelined  │        │ Shared   │        │ Simple   │
  │ Out-of-ord │        │ bus,sync │        │ reg I/F  │
  └────────────┘        └──────────┘        └──────────┘
  CPU, GPU, DMA       On-chip memory      UART, I2C, GPIO
```

## AXI (Advanced eXtensible Interface)

AXI4 is the backbone of modern SoCs (Cortex-A, Mali, etc.). Its defining feature is **separate read and write channels**, each with independent handshakes.

**Five AXI4 channels:**

| Channel | Direction | Purpose |
|---------|-----------|---------|
| AW | Master → Slave | Write address + burst info |
| W | Master → Slave | Write data |
| B | Slave → Master | Write response |
| AR | Master → Slave | Read address + burst info |
| R | Slave → Master | Read data + response |

**Key AXI concepts for virtual prototyping:**

- **Outstanding transactions**: Multiple addresses can be issued before responses arrive. A virtual bus model must track in-flight transactions per ID.
- **Burst types**: FIXED, INCR, WRAP. INCR is by far the most common; model it by incrementing address by beat size × beat count.
- **ARID / AWID / BID / RID**: Transaction IDs allow out-of-order completion. A simple model may serialize; a high-fidelity model must reorder.

```cpp
// Simplified AXI read modeled as a single TLM b_transport
tlm::tlm_generic_payload txn;
txn.set_command(tlm::TLM_READ_COMMAND);
txn.set_address(0x2000'0000);
txn.set_data_length(4 * BURST_LEN); // 4-byte beats
sc_time delay = SC_ZERO_TIME;
initiator_socket->b_transport(txn, delay);
```

## AHB (Advanced High-performance Bus)

AHB is a **shared, pipelined, single-master-at-a-time** bus. It is simpler than AXI: there is one address phase followed by one data phase. An arbiter grants the bus to one master per cycle.

**TLM modeling of AHB pipeline:**

- Address phase and data phase overlap by one cycle. Model this by adding 1-cycle latency for the pipelining overlap.
- Burst support: SINGLE, INCR, WRAP4/8/16. Model by issuing multiple b_transport calls with incrementing addresses, or as a single large transaction.
- Split transactions (HSPLIT) are rarely modeled at TLM; they are an RTL concern.

## APB (Advanced Peripheral Bus)

APB is the simplest member. It is **non-pipelined**, with a fixed 2-cycle access (SETUP + ACCESS). It connects low-bandwidth peripherals.

```cpp
// APB timing model: every access costs exactly 2 cycles
void apb_b_transport(tlm::tlm_generic_payload& txn, sc_time& delay) {
    delay += 2 * CLK_PERIOD; // SETUP + ACCESS phase
    // ... read/write register file
    txn.set_response_status(tlm::TLM_OK_RESPONSE);
}
```

## Choosing the Right Protocol Model

| If you need... | Use... |
|----------------|--------|
| CPU-to-DDR with max bandwidth | AXI4 (or AXI4-Lite for control) |
| On-chip SRAM, DMA, interrupt ctrl | AHB-Lite |
| Peripheral register config | APB |
| Bridge between AXI and APB | AXI-to-APB bridge component |

## Protocol Conversion at Bridges

An AXI-to-APB bridge converts wide, pipelined AXI bursts into sequential 2-cycle APB accesses. In a TLM model this means:

1. Accept an AXI burst transaction (e.g., 4 × 32-bit beats).
2. Split it into 4 individual APB transactions internally.
3. Accumulate latency: `delay += 4 * 2 * CLK_PERIOD`.
4. Return a single TLM OK response.

## Common Pitfalls

- **Modeling AXI as APB**: Missing out-of-order capability may hide memory-ordering bugs early in bring-up.
- **Ignoring byte enables on AHB**: HSIZE and HBSTRB control which bytes are valid; blindly writing all bytes causes silent corruption.
- **Missing the APB SETUP phase**: Modeling APB as 1-cycle makes peripheral register access 2× faster than reality.

**Interview answer:** "AXI supports out-of-order, pipelined read/write channels for high-bandwidth masters; AHB is a shared pipelined bus with one master at a time; APB is a simple 2-cycle non-pipelined bus for slow peripherals. A virtual prototype normally models all three, connected by bridges."
