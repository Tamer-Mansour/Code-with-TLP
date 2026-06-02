# Platform Bring-Up Order

Bring-up is the process of getting a new virtual platform to the point where it runs real firmware. Done in the wrong order it becomes a debugging nightmare — you cannot tell whether the CPU, bus, or peripheral is broken. Done correctly, each step produces a clear pass/fail signal.

## The Five-Step Bring-Up Ladder

```
Step 5: Run real firmware (RTOS / bare-metal app)
Step 4: Run a peripheral driver test
Step 3: Run a memory test
Step 2: Run a bus transaction test
Step 1: Run the wiring smoke test
```

Work bottom-up. Never advance to the next step until the current one passes cleanly.

## Step 1 — Wiring Smoke Test

Call `sc_start(SC_ZERO_TIME)` without any firmware loaded. SystemC will:

- Complete elaboration.
- Report unbound sockets as fatal errors.
- Report duplicate bindings.

```cpp
int sc_main(int argc, char *argv[]) {
    // ... instantiate and bind ...
    sc_core::sc_start(sc_core::SC_ZERO_TIME); // wiring check only
    std::cout << "Wiring OK\n";
    return 0;
}
```

If this passes, every socket is bound and the address map is conflict-free.

## Step 2 — Bus Transaction Test

Write a minimal SC_THREAD that issues hand-crafted TLM transactions directly to the bus — no ISS required:

```cpp
void bus_test::run() {
    tlm::tlm_generic_payload txn;
    sc_core::sc_time delay = sc_core::SC_ZERO_TIME;
    uint32_t wdata = 0xDEADBEEF, rdata = 0;

    // Write to RAM
    txn.set_command(tlm::TLM_WRITE_COMMAND);
    txn.set_address(RAM_BASE + 0x10);
    txn.set_data_ptr(reinterpret_cast<uint8_t*>(&wdata));
    txn.set_data_length(4);
    bus.b_transport(txn, delay);
    assert(txn.get_response_status() == tlm::TLM_OK_RESPONSE);

    // Read back
    txn.set_command(tlm::TLM_READ_COMMAND);
    txn.set_data_ptr(reinterpret_cast<uint8_t*>(&rdata));
    bus.b_transport(txn, delay);
    assert(rdata == 0xDEADBEEF);

    SC_REPORT_INFO("bus_test", "PASS");
    sc_core::sc_stop();
}
```

## Step 3 — Memory Test

Load a simple memory test binary — a tight loop that writes a pattern to all of RAM and reads it back. If the ISS is not ready, drive the transactions manually as in Step 2.

## Step 4 — Peripheral Driver Test

Test each peripheral with the smallest possible firmware that exercises it:

| Peripheral | Minimal test |
|---|---|
| UART | Write `'A'` to TX register; expect `'A'` on stdout |
| Timer | Enable counter; wait; read counter; assert non-zero |
| GPIO | Toggle output pin; read input pin; compare |
| Interrupt | Enable IRQ; trigger peripheral; ISR increments counter |

These tests are faster to run than a full firmware image and pinpoint the exact peripheral with a problem.

## Step 5 — Full Firmware

Run the real firmware (bare-metal app or RTOS). Common first targets:

- **Hello World** via UART — confirms ISS, bus, memory, and UART all work end-to-end.
- **RTOS tick** — confirms the timer IRQ and context-switch path.
- **LED blink** — confirms GPIO toggle timing.

## Debugging During Bring-Up

| Symptom | Likely cause | Debug action |
|---|---|---|
| Simulation hangs at `sc_start` | Unbound socket detected at elaboration | Check binding order; run wiring smoke test |
| Bus returns `TLM_ADDRESS_ERROR_RESPONSE` | Address not in any decode range | Print bus decode table; check base/size |
| ISS fetches 0xFFFFFFFF | Firmware not loaded into ROM | Verify load_binary was called before sc_start |
| Peripheral IRQ never fires | IRQ signal not connected | Check `irq.bind()` in sc_main |
| Timer reads 0 always | Reset not deasserted before firmware runs | Check reset sequence timing |

## Bring-Up Checklist

- [ ] Wiring smoke test passes (zero-time start).
- [ ] Manual write/read round-trip through each memory region passes.
- [ ] Each peripheral responds to its base address with correct reset values.
- [ ] Each interrupt line is connected and fires at least once under a minimal test.
- [ ] Hello World runs successfully via UART.

**Interview answer:** VP bring-up is a five-step ladder: wiring smoke test, bus transaction test, memory test, peripheral driver tests, then full firmware. Each step isolates one layer so failures are unambiguous. The most common early failure is an unloaded firmware image or a disconnected interrupt line.
