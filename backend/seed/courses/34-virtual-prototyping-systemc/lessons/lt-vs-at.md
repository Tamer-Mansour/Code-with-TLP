# LT vs AT: Speed and Accuracy Tradeoffs

Choosing between Loosely-Timed (LT) and Approximately-Timed (AT) is one of the first architectural decisions when building a virtual prototype. The right choice depends on what question the model must answer.

## The Fundamental Tradeoff

| Dimension | LT | AT |
|---|---|---|
| Simulation speed | Very fast (1 context switch / transaction) | Moderate (2-4 context switches / transaction) |
| Timing accuracy | Low — no pipelining visible | Moderate — pipelining captured |
| Protocol fidelity | None (single blocking call) | Partial (phases, not all bus signals) |
| Implementation effort | Low | High |
| Best use case | Software bring-up, functional testing | Performance estimation, interconnect tuning |

## Speed: Why LT Is Faster

Each `b_transport` call in LT is a direct C++ function call with no scheduler involvement (unless the target calls `wait()`). A single 32-bit memory read touches perhaps 20 lines of C++.

The same transaction in AT triggers two to four scheduler events:
1. `nb_transport_fw` → `TLM_UPDATED` (BEGIN_REQ)
2. Response event fires → `nb_transport_bw` (BEGIN_RESP)
3. Initiator acknowledges → `nb_transport_fw` (END_RESP)

SystemC's scheduler must process each event delta. On a benchmark with 10 million bus transactions, this overhead is measurable — LT often runs 5-20x faster than AT for the same functional model.

```
Benchmark: 10M random 32-bit reads, simple SRAM target
LT simulation time :  8 s
AT simulation time : 62 s
Speedup            : ~7.8x
```

## Accuracy: What AT Reveals That LT Cannot

LT models the entire transaction as atomic from the scheduler's perspective. A pipelined bus (AXI, CHI) where the master issues four outstanding reads before the first response arrives **cannot** be captured correctly in LT.

AT's phased protocol lets you model:
- **Request/response pipeline depth** — how many transactions are in flight simultaneously.
- **Back-pressure** — a busy target asserts END_REQ late, stalling the initiator.
- **Latency hiding** — out-of-order responses that arrive while the CPU executes other instructions.

```
LT view of 4 pipelined reads (each 20 ns):
  T=0   Read A done (20 ns total)
  T=20  Read B done
  T=40  Read C done
  T=60  Read D done
  Total perceived latency = 80 ns

AT view of 4 pipelined reads (4 outstanding, 20 ns each):
  T=0   BEGIN_REQ for A, B, C, D issued back-to-back
  T=20  Response A arrives
  T=21  Response B arrives
  ...
  Total perceived latency = ~23 ns  (pipeline benefit captured)
```

## Accuracy Is Not "Correctness"

AT is not cycle-accurate. It does not model clock edges, individual bus lanes, or handshake signal timing. The phases represent **events**, not waveforms. When detailed timing is needed for DDR controller tuning or cache coherence protocol verification, a cycle-accurate or RTL model is required.

## Decision Guide

Use **LT** when:
- Running OS boot or software test suites that need millions of transactions.
- The memory subsystem timing has negligible impact on the software behavior being tested.
- Simulation speed is the primary constraint.

Use **AT** when:
- Building a performance model to estimate bandwidth or latency of a new bus topology.
- Modeling a DMA engine, GPU, or NIC where multiple outstanding transactions are the norm.
- Feeding a performance database for early microarchitecture decisions.

## Mixed LT/AT Models

TLM-2.0 allows LT and AT components to coexist via **protocol converters** (adapters that sit between an LT initiator socket and an AT target socket or vice versa). This is common in practice: the CPU model is LT (speed), while the interconnect is AT (accuracy).

> **Interview answer:** "LT has one context switch per transaction and is 5-20x faster, but cannot model pipelined overlap. AT's phased protocol captures pipeline depth and back-pressure but adds scheduler overhead. Use LT for software bring-up, AT for performance modeling."
