# Finite State Machines in Hardware

A **Finite State Machine (FSM)** is a sequential circuit that moves through a finite number of defined states, transitioning based on inputs. FSMs model any behavior that depends on history — protocol handshakes, instruction sequencing, memory controllers, and CPU control units are all FSMs at heart.

## Two FSM Models

| Model | Output depends on | When to use |
|-------|------------------|-------------|
| **Moore** | Current state only | Simpler, glitch-free outputs |
| **Mealy** | Current state + current inputs | Fewer states needed, faster response |

Moore outputs change only at clock edges (safe). Mealy outputs can change immediately when inputs change (faster but can glitch).

## FSM Anatomy

Every FSM has:
1. **State register** — flip-flops encoding the current state
2. **Next-state logic** — combinational function of (state, inputs)
3. **Output logic** — combinational (Mealy) or state-only (Moore)

```
             ┌─────────────┐
Inputs ─────►│  Next-State │──► Next State
             │   Logic     │          │
             └─────────────┘          │
                   ▲                  ▼
             ┌─────┴───────────────────┐
             │   State Register        │
             │   (D Flip-Flops)        │
             └─────────────────────────┘
                   │
                   ▼
             ┌─────────────┐
             │Output Logic │──► Outputs
             └─────────────┘
```

## Encoding States

For N states, you need `ceil(log2(N))` flip-flops. Common encodings:

| Encoding | Bits needed | Transition speed | Power |
|----------|-------------|-----------------|-------|
| Binary | ceil(log2 N) | Medium | Low |
| One-hot | N | Fast (simple logic) | Higher |
| Gray code | ceil(log2 N) | Medium | Low (1-bit transitions) |

CPUs with simple controllers often use binary encoding. High-speed protocols use one-hot for fastest decode.

## Worked Example: Traffic Light Controller (Moore FSM)

States: `RED`, `GREEN`, `YELLOW`
Input: `timer_expired` (1 = time for this phase is done)

State diagram:
```
  ┌──────────────────────────────┐
  │                              │
  ▼   timer_expired=1           │
[RED] ──────────────────► [GREEN]
  ▲                           │
  │                 timer_expired=1
  │                           ▼
  └──────────── [YELLOW] ◄────┘
      timer_expired=1
```

Truth table (2-bit state encoding: RED=00, GREEN=01, YELLOW=10):

| State | timer | Next State | Output (R,Y,G) |
|-------|-------|------------|----------------|
| RED    | 0 | RED    | 1,0,0 |
| RED    | 1 | GREEN  | 1,0,0 |
| GREEN  | 0 | GREEN  | 0,0,1 |
| GREEN  | 1 | YELLOW | 0,0,1 |
| YELLOW | 0 | YELLOW | 0,1,0 |
| YELLOW | 1 | RED    | 0,1,0 |

Note: In Moore, outputs depend only on state, not on `timer`.

## Worked Example: Simple Protocol FSM in C

```c
typedef enum { IDLE, START, DATA, STOP } State;

State state = IDLE;
int data_bits = 0;

void clock_tick(int rx) {
    switch (state) {
        case IDLE:
            if (rx == 0) state = START;   // start bit detected
            break;
        case START:
            state = DATA;
            data_bits = 0;
            break;
        case DATA:
            // collect bit, advance
            data_bits++;
            if (data_bits == 8) state = STOP;
            break;
        case STOP:
            state = IDLE;
            break;
    }
}
```

This is a Mealy-style FSM in software — the UART receiver's exact logic.

## FSM Minimization

Two states are **equivalent** if:
1. They produce the same output for all inputs.
2. They transition to equivalent next states for all inputs.

Equivalent states can be merged to reduce the state register size. This is the hardware analog of dead-code elimination.

## CPU Control Unit as FSM

The RISC-V multi-cycle control unit cycles through states like:

```
FETCH → DECODE → EXECUTE → MEMORY ACCESS → WRITE BACK → (FETCH)
```

Each state asserts a specific set of control signals. The state register holds the current pipeline stage; the next-state logic is the instruction decoder feeding the sequencer.

## Common Pitfalls

- **Missing reset state**: without an explicit reset, the state register may power up in an undefined state. Always define the initial state and tie it to a synchronous or asynchronous reset.
- **Unreachable states**: binary encoding may create states not in your design (e.g., state 3 with only states 0,1,2 defined). Add explicit transitions to a safe state for these.
- **Mealy glitches**: Mealy outputs can glitch when inputs change mid-cycle. Register Mealy outputs through a flip-flop if downstream logic is sensitive.
- **State explosion**: FSMs grow exponentially with features. Hierarchical (nested) FSMs or datapath+control partitioning keep complexity manageable.

## Interview Answer

> "An FSM is a sequential circuit with a finite set of states, a next-state function of (state, inputs), and an output function. Moore outputs depend only on state; Mealy outputs also depend on inputs. CPU control units, protocol engines, and memory controllers are all FSMs — the state register is the flip-flops, and the next-state logic is the instruction decoder."
