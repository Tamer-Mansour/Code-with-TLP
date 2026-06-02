# SC_METHOD vs SC_THREAD: When to Use Which

Choosing between `SC_METHOD` and `SC_THREAD` is one of the first design decisions you make in every SystemC module. Getting it right makes your model accurate, synthesisable, and fast to simulate.

## Decision Matrix

| Criterion | SC_METHOD | SC_THREAD |
|---|---|---|
| Needs to suspend mid-run | No | Yes |
| Models combinational logic | Best fit | Possible but wasteful |
| Models sequential / clocked logic | Awkward (state vars needed) | Natural fit |
| Uses `wait()` | Forbidden | Required for suspension |
| Stack saved between activations | No | Yes |
| Simulation overhead | Low | Higher (coroutine switch) |
| RTL synthesis (HLS) | Combinational output | Sequential output |
| Typical trigger | Any signal change | Clock edge or timed event |

## Use SC_METHOD When…

- The output depends **only on current inputs** (pure combinational function).
- The logic completes in a single "instant" with no multi-step protocol.
- You want **maximum simulation performance** for a large number of simple reactive blocks.
- You are targeting synthesis and want combinational inference.

```cpp
// Good SC_METHOD: one-shot combinational decode
void decode_opcode() {
    sc_uint<6> op = instr.read().range(31, 26);
    alu_op.write(op == 0x00 ? ALU_ADD : ALU_NOP);
}
```

## Use SC_THREAD When…

- The behaviour spans **multiple clock cycles** (pipelines, FSMs, protocols).
- The process needs to **remember where it was** between clock edges.
- Straight-line, readable code is more important than raw simulation speed.
- You are modelling bus transactions (AXI, AHB, SPI, I2C, UART).

```cpp
// Good SC_THREAD: AXI write transaction
void axi_write(uint32_t addr, uint32_t data) {
    awvalid.write(1); awaddr.write(addr);
    do { wait(); } while (!awready.read());  // wait for handshake
    awvalid.write(0);

    wvalid.write(1); wdata.write(data);
    do { wait(); } while (!wready.read());
    wvalid.write(0);
}
```

Implementing this with `SC_METHOD` would require an explicit state machine enum, a state variable, and a case statement — all added complexity.

## The Hybrid Pattern

Sometimes a module needs both: an `SC_METHOD` for fast combinational outputs and an `SC_THREAD` for the clocked control path.

```cpp
SC_CTOR(PipelineStage) {
    SC_METHOD(forward_data);       // combinational bypass
    sensitive << data_in;

    SC_THREAD(latch_on_clock);     // register on clock edge
    sensitive << clk.pos();
}
```

This mirrors how real RTL designs separate combinational and sequential always blocks.

## Performance Guidance

In a large SoC simulation with tens of thousands of processes, `SC_METHOD` processes can run **2–5x faster** than equivalent `SC_THREAD` processes because no coroutine context switch is needed. Profile before switching, but as a rule:

- Every clock-domain crossing or bus interface → `SC_THREAD`.
- Every decode, mux, or glue logic block → `SC_METHOD`.

## Common Interview Trap

Interviewers sometimes ask: *"Can an SC_METHOD model a register?"* The answer is yes — by storing state in a **module-level variable** — but it requires careful hand-coding of the "previous state" vs "next state" logic:

```cpp
bool q_reg = false;

void dff() {
    if (clk.read() == 1)   // only acts on rising edge
        q_reg = d.read();
    q.write(q_reg);
}
```

This works but is fragile compared to the natural `SC_THREAD` equivalent. In practice, clocked registers always use `SC_THREAD` (or `SC_CTHREAD`).

> **Interview answer:** Use `SC_METHOD` for purely combinational logic that computes a result instantly from current inputs. Use `SC_THREAD` for any sequential behaviour that must suspend across multiple clock cycles — protocols, state machines, pipelines. `SC_METHOD` has lower overhead; `SC_THREAD` yields more readable multi-cycle code.
