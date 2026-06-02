# Bus Arbitration and Mastering

A shared bus can only carry one transaction at a time. When multiple devices want to use the bus simultaneously, **arbitration** decides who wins. The winner becomes the **bus master** for the duration of that transaction.

## Bus Masters vs. Bus Slaves

- **Bus master**: a device capable of initiating a transaction — driving the address and control lines. CPUs and DMA controllers are masters.
- **Bus slave** (target): a device that responds to transactions but never initiates them. Memory chips, most simple peripherals.
- Some devices (e.g., a DMA controller) can act as both master and slave at different times.

## The Arbitration Problem

Suppose the CPU and a DMA controller both want the bus at the same clock cycle. Without arbitration, both would drive the address lines simultaneously — an electrical conflict (bus fight) that can damage hardware. Arbitration prevents this by ensuring only one master drives the bus at any time.

## Arbitration Schemes

### 1. Daisy-Chain Arbitration

Devices are connected in a chain. The arbiter sends a `BUS GRANT` signal that ripples down the chain. The first device in the chain that is requesting the bus captures the grant and stops passing it onward.

```
Arbiter ──GRANT──► Device 1 ──► Device 2 ──► Device 3
                   (captures if requesting, else passes)
```

- **Priority:** fixed by position — Device 1 always wins over Device 2.
- **Advantage:** simple, minimal wires.
- **Disadvantage:** low-priority devices can starve; a broken link blocks all lower devices.

### 2. Centralized Parallel Arbitration

Every potential master has its own dedicated `REQUEST` and `GRANT` line to a central arbiter. The arbiter evaluates all pending requests and grants the bus to one device each cycle.

```
CPU    ──REQ──► [Arbiter] ──GNT──► CPU
DMA    ──REQ──►            ──GNT──► DMA
GPU    ──REQ──►            ──GNT──► GPU
```

The arbiter can implement any policy:
- **Fixed priority**: always favor the CPU over DMA.
- **Round-robin**: rotate among requestors fairly.
- **Weighted round-robin**: give high-priority devices more turns.
- **Least recently used (LRU)**: grant to the device that waited longest.

**Interview answer:** Centralized parallel arbitration gives each bus master dedicated request/grant lines to an arbiter that selects one winner per cycle using a configurable policy (fixed priority, round-robin, etc.).

### 3. Distributed Arbitration

No central arbiter exists. Each device broadcasts its priority ID onto dedicated arbitration lines. All devices simultaneously read the bus and determine whether they won without central coordination. SCSI uses a form of this — each device drives its own bit and reads back who won.

## The BUSREQ / BUSACK Handshake

On many classic buses (Z80, ISA), the CPU is the default master. A peripheral that wants the bus uses a two-signal handshake:

1. Peripheral asserts **BUSREQ** (bus request).
2. CPU finishes its current cycle, then asserts **BUSACK** (bus acknowledge) and tristate its address/data/control outputs.
3. Peripheral takes control, performs its transaction(s).
4. Peripheral deasserts BUSREQ.
5. CPU deasserts BUSACK and reclaims the bus.

```c
// Pseudocode for a DMA controller
assert(BUSREQ);
wait_for(BUSACK);
drive_address(src);
assert(READ);
latch_data();
drive_address(dst);
assert(WRITE);
output_data();
deassert(BUSREQ);
```

## Fairness and Starvation

Fixed-priority arbitration can cause **starvation** — a low-priority device never gets the bus if higher-priority devices continuously request it. Round-robin arbitration prevents starvation but may allow a high-priority device to wait longer than desired. Most real systems use a **priority + aging** hybrid: each request's effective priority increases the longer it waits.

## Split Transactions

Modern high-performance buses (AXI, PCIe) use **split transactions**: the master issues a request and releases the bus immediately. When the data is ready, the slave re-requests the bus to deliver the response. This prevents slow devices from tying up the bus during the latency gap and allows pipelining of multiple outstanding transactions — effectively removing the need for traditional arbitration in a round-robin sense.

## Common Pitfall

Students confuse bus arbitration with CPU scheduling. Bus arbitration operates at the hardware level, resolving which device drives the bus lines in the *current clock cycle*. CPU scheduling is a software concern that runs on timescales millions of times longer.
