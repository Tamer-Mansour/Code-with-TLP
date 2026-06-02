# Structural Hazards

A **structural hazard** occurs when two or more instructions in different pipeline stages simultaneously require the same physical hardware resource and the hardware cannot satisfy both requests in the same clock cycle. Unlike data hazards, structural hazards are entirely about the microarchitecture — they arise from design choices about how many copies of a resource exist, not from the values those resources hold.

## Classic Example: A Unified Memory

The textbook case is a single-port memory shared between the Instruction Fetch (IF) stage and the Memory Access (MEM) stage. In cycle N:

- The instruction in IF wants to **read** the memory to fetch the next opcode.
- The instruction in MEM wants to **read or write** data memory for a load or store.

Both cannot use the same memory bus in the same cycle. One must wait.

```
Cycle:    1    2    3    4    5    6
add       IF   ID   EX  MEM   WB
lw             IF   ID   EX  [stall] MEM  WB
sub                 IF   ID   [stall] EX  MEM  WB
```

The stall propagates through the entire pipeline behind the load.

## The Standard Fix: Harvard Architecture

Modern processors avoid this by maintaining **separate instruction and data caches** (the Harvard memory model). The L1-I cache serves IF; the L1-D cache serves MEM. Because they are physically distinct, both stages can proceed simultaneously with no conflict.

| Design | Structural Hazard? | Cost |
|---|---|---|
| Single unified cache | Yes — load/store vs fetch | One stall cycle per conflict |
| Split I-cache / D-cache | No | Additional area (two caches) |

## Register File Port Conflicts

A subtler structural hazard involves the register file. A five-stage pipeline wants to **write** a result (WB stage) and **read** two source operands (ID stage) in the same cycle. If the register file only has one read port and one write port, this is a conflict.

The solution is to build the register file with **two read ports and one write port**, or more commonly, to handle the WB write in the first half of the clock cycle and the ID read in the second half. This is called **register-file forwarding** or **internal forwarding** and it eliminates the hazard with no stall cost.

## Functional Unit Conflicts

In processors with a single, non-pipelined divide unit, two division instructions close together create a structural hazard because the first division still occupies the unit when the second arrives. Mitigations include:

- **Pipelining** the functional unit itself so it accepts a new input every cycle.
- **Replicating** the unit — having two dividers.
- **Stalling** the second instruction until the unit is free (the cheapest implementation but the worst performance).

## Structural vs Data Hazards

Students sometimes confuse the two. The key distinction:

- **Structural hazard:** the hardware resource itself is unavailable — independent instructions can still collide.
- **Data hazard:** the *value* in a register or memory location is not yet correct — only instructions with a producer-consumer relationship collide.

## Pitfall: Ignoring Structural Hazards at the Microarchitecture Level

When reading timing diagrams, always ask: "Does this pipeline have the hardware to service both stages simultaneously?" Textbook pipelines often assume Harvard memory and sufficient register file ports, making structural hazards invisible. Real designs must budget area for the extra ports and caches.

## Interview Answer

> "A structural hazard happens when two instructions in different pipeline stages compete for the same hardware resource at the same time. The classic fix is to duplicate the resource — for example, using separate instruction and data caches so that fetch and memory access never conflict."
