# Signal vs Transaction: Two Communication Styles

At the heart of the RTL vs TLM distinction is a communication philosophy question: should components talk to each other by wiggling wires, or by passing messages? Both approaches model the same hardware reality — they just expose different layers of it.

## Signal-Level Communication

In RTL, every interface is a bundle of typed signals. Data flows by the sender driving signal values and the receiver sampling them at the right clock edge. The protocol — the sequence of signal changes that makes a transfer valid — is part of the simulation itself.

Consider an AXI4 write channel in RTL:

```cpp
// RTL AXI write address channel (simplified)
sc_out<sc_uint<32>> awaddr;   // write address
sc_out<sc_uint<8>>  awlen;    // burst length
sc_out<bool>        awvalid;  // address valid
sc_in<bool>         awready;  // slave is ready

// Initiating a write:
awaddr.write(0x4000);
awlen.write(3);           // 4-beat burst
awvalid.write(true);
wait(clk.posedge_event());
while (!awready.read())   // protocol handshake
    wait(clk.posedge_event());
awvalid.write(false);
```

Every signal transition is an event. The simulator must evaluate all logic sensitive to `awvalid` every time it changes. A single 4-beat AXI burst could easily generate 50–100 signal events in RTL.

## Transaction-Level Communication

In TLM, the same write is a single generic payload passed through a socket. The protocol is not simulated; it is approximated with a time annotation.

```cpp
// TLM AXI write (same 4-beat burst)
tlm::tlm_generic_payload trans;
sc_core::sc_time delay(40, SC_NS);  // approximated burst cost

unsigned char data[16];
// ... fill data ...

trans.set_command(tlm::TLM_WRITE_COMMAND);
trans.set_address(0x4000);
trans.set_data_ptr(data);
trans.set_data_length(16);  // 4 beats × 4 bytes

socket->b_transport(trans, delay);
// delay now holds total accumulated latency
```

One event instead of hundreds. The `data` array arrives at the target with the correct contents, but no handshake signals were ever toggled.

## What Each Style Reveals and Hides

| Observable | Signal-Level RTL | Transaction-Level TLM |
|---|---|---|
| Data value | Yes | Yes |
| Transfer direction | Yes | Yes |
| Burst length | Yes (encoded in signals) | Yes (in payload fields) |
| Handshake timing | Yes — exact cycles | No — approximated delay |
| Back-pressure from slave | Yes — `ready` going low | No — embedded in delay annotation |
| Bus arbitration cycles | Yes | No |
| Wire contention / glitches | Yes (with delays) | No |
| Error responses | Yes (per-protocol signals) | Yes (`tlm_response_status`) |

## The Transactor: Bridging the Gap

When an RTL block needs to talk to a TLM model (common in virtual platforms that wrap one RTL IP in a TLM environment), a transactor converts between the two styles.

```
[TLM Initiator]
     |
     | b_transport(payload)
     v
[Transactor / Bus Functional Model]
     |    decomposes payload into signal wiggles
     v
[RTL Target — sees real signal transitions]
```

The transactor "unzips" a transaction into the sequence of signals that the RTL target expects, then "zips" the RTL response back into a TLM return value. Writing accurate transactors is non-trivial; every quirk of the bus protocol must be re-implemented.

## Analogies That Help

- **Signal-level is like Morse code** — every bit is explicit, every pulse matters, and the receiver must decode the protocol in real time.
- **Transaction-level is like email** — you compose a message, send it, and the network infrastructure (approximated by the delay) handles the rest. You don't care about individual packet headers.

## When Signal-Level Is Irreplaceable

- **DFT (Design for Test)** — scan chains require bit-level control of every flip-flop.
- **Analog/mixed-signal interfaces** — you cannot abstract away a PLL or an ADC meaningfully at TLM level.
- **Timing closure** — only signal-level simulation with SDF back-annotation can verify setup and hold times.
- **Power analysis** — switching activity at the signal level feeds power estimation tools.

## When Transaction-Level Wins

- **Software bring-up** — a driver only cares that address X returns data Y, not which cycle `awready` went high.
- **System integration** — verifying that 10 IP blocks cooperate correctly is impractical at RTL speeds.
- **Memory subsystem modeling** — a DDR controller can be approximated accurately enough for cache studies without full RTL.

## Interview Answer

> "Signal-level communication wiggles individual wires cycle by cycle and captures every protocol handshake. Transaction-level communication passes a payload object through a function call with a time annotation, hiding the handshake and dramatically reducing simulation events. Transactors bridge the two styles when mixed-level simulation is needed."
