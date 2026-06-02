# Registers and Counters from Flip-Flops

A single D flip-flop stores one bit. Connect several in parallel to store a word, or in series to shift data, and you have a **register**. Add feedback logic so the stored value increments automatically and you have a **counter**. These two primitives are everywhere in CPU datapaths.

## N-Bit Parallel Register

An N-bit register is simply N D flip-flops sharing a common clock (and usually a common enable and reset):

```
D[7:0] ──►[ 8 × D FF ]──► Q[7:0]
                 ▲
               CLK
```

Operations:
- **Load**: when `LOAD=1`, Q latches D on the next rising clock edge.
- **Hold**: when `LOAD=0`, Q feeds back to D (Q does not change).
- **Reset**: synchronous or asynchronous clear sets all Q bits to 0.

**CPU context**: Every general-purpose register in the RISC-V register file (x0–x31) is a 32-bit or 64-bit parallel register. The Program Counter (PC) is also a register — it just has special increment logic.

## Shift Register

In a **serial-in, serial-out (SISO)** shift register, each flip-flop's Q drives the next flip-flop's D:

```
Serial IN ──► [D FF] ──► [D FF] ──► [D FF] ──► [D FF] ──► Serial OUT
                ▲           ▲           ▲           ▲
              CLK         CLK         CLK         CLK
```

After N clock cycles, the serial input has been shifted through all N stages. Variants:

| Type | Description |
|------|-------------|
| SISO | Serial in, serial out — pure delay line |
| SIPO | Serial in, parallel out — serial-to-parallel conversion |
| PISO | Parallel in, serial out — used in serial communication (UART, SPI) |
| PIPO | Parallel in, parallel out — universal shift register (most common) |

**CPU context**: Barrel shifters (used for `SLLI`, `SRLI`, `SRAI` in RISC-V) can be built as a cascade of MUX-selected shift registers.

## Binary Ripple Counter

Chain T flip-flops (or JK with J=K=1) so each stage toggles when the previous stage overflows:

```
CLK ──► [T FF] ──► [T FF] ──► [T FF] ──► [T FF]
          Q0          Q1          Q2          Q3
```

Q0 toggles every cycle, Q1 every 2 cycles, Q2 every 4 cycles, Q3 every 8 cycles.
The 4-bit count sequence: `0000` → `0001` → … → `1111` → `0000`.

**Ripple problem**: each stage must wait for the previous to settle. With 32 stages the cumulative delay is `32 × t_FF`, limiting speed. This is a purely asynchronous counter.

## Synchronous Binary Counter

All flip-flops share the same clock. Combinational AND logic computes each flip-flop's enable:

```
Q0 always toggles.
Q1 toggles when Q0 = 1.
Q2 toggles when Q0 = 1 AND Q1 = 1.
Q3 toggles when Q0 = 1 AND Q1 = 1 AND Q2 = 1.
```

```
T0 = 1
T1 = Q0
T2 = Q0 · Q1
T3 = Q0 · Q1 · Q2
```

All flip-flops update simultaneously on the clock edge — no ripple delay. Maximum speed is limited only by the combinational AND chain, which grows logarithmically (use a carry-lookahead structure for large counters).

## Modulo-N Counter

A counter that resets after N counts. Implement by detecting the state `N` and asynchronously (or synchronously) resetting:

```python
# Behavioral model of a modulo-5 counter
def modulo_n_counter(n, cycles):
    count = 0
    for _ in range(cycles):
        print(count)
        count = (count + 1) % n
```

```
Output for n=5, cycles=7: 0 1 2 3 4 0 1
```

**CPU context**: The performance counter (`mcycle` in RISC-V) is a 64-bit synchronous counter that wraps at 2^64.

## Ring Counter and Johnson Counter

- **Ring counter**: a single 1 circulates through N flip-flops — produces N unique one-hot states. Used in sequencers.
- **Johnson counter** (twisted-ring): the complement of the last stage feeds back to the first — produces 2N unique states with N flip-flops.

## Worked Example: 4-bit Up/Down Counter in C (Simulation)

```c
#include <stdio.h>

int main(void) {
    uint8_t count = 0;
    int direction = 1; // 1=up, -1=down

    for (int cycle = 0; cycle < 20; cycle++) {
        printf("Cycle %2d: %d (%04b)\n", cycle, count, count);
        count = (count + direction) & 0x0F; // 4-bit mask
        if (count == 0xF) direction = -1;
        if (count == 0x0) direction =  1;
    }
    return 0;
}
```

## Common Pitfalls

- **Ripple counter glitches**: intermediate states during ripple propagation can cause decoders downstream to briefly assert wrong outputs ("hazard glitches"). Use synchronous counters in clocked systems.
- **Counter reset glitches**: asynchronous reset in a modulo-N counter using a NAND gate fires only for one propagation delay — that spike may be too short to reliably reset all flip-flops.
- **Shift register initialization**: undefined initial state causes undefined behavior in SISO applications. Always reset or preload.

## Interview Answer

> "A register is N flip-flops sharing a clock — it stores a word. A synchronous counter adds combinational carry logic so all flip-flops update simultaneously on one clock edge, avoiding the cumulative delay of a ripple counter. Both primitives appear directly in CPU register files and program-counter increment logic."
