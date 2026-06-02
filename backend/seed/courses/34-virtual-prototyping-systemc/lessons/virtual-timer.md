# Modeling a Virtual Timer

Timers are among the most fundamental peripherals in any embedded system. The OS tick, watchdog, PWM generation, and timeout detection all depend on a hardware timer. In a virtual prototype, a timer model must advance in **simulation time** — not host wall-clock time — so that software delay loops, `usleep()`, and RTOS ticks all execute correctly regardless of host CPU speed.

## What a Hardware Timer Does

A hardware timer is essentially a counter that:
1. Counts up (or down) at a known frequency derived from the system clock.
2. Compares its counter value against a **compare register**.
3. Fires an interrupt when the counter matches (or overflows).
4. Optionally reloads to a preset value and continues (periodic mode).

## Register Map (Generic Timer)

| Offset | Register | Description |
|---|---|---|
| 0x00 | CTRL | Enable, mode (one-shot/periodic), interrupt enable |
| 0x04 | PERIOD | Reload value (ticks between interrupts) |
| 0x08 | COUNTER | Current counter value (read-only) |
| 0x0C | STATUS | Interrupt pending flag; write 1 to clear |

## SystemC Timer Model

```cpp
SC_MODULE(VirtualTimer) {
    sc_in<bool>  clk;
    sc_out<bool> irq;
    tlm_utils::simple_target_socket<VirtualTimer> socket;

    uint32_t ctrl, period, counter, status;
    sc_time  tick_period;   // simulation time per tick

    void timer_thread() {
        while (true) {
            wait(tick_period);          // advance simulation time
            if (!(ctrl & CTRL_EN)) continue;

            counter++;
            if (counter >= period) {
                counter = (ctrl & CTRL_PERIODIC) ? 0 : counter;
                status |= STATUS_PENDING;
                if (ctrl & CTRL_IRQ_EN) {
                    irq.write(true);    // assert interrupt
                    wait(SC_ZERO_TIME);
                    irq.write(false);   // pulse (edge-trigger)
                }
            }
        }
    }

    void b_transport(tlm::tlm_generic_payload& trans, sc_time& delay);

    SC_CTOR(VirtualTimer) : socket("socket") {
        tick_period = sc_time(1, SC_US);  // 1 MHz timer
        SC_THREAD(timer_thread);
    }
};
```

## The Tick Period and Simulation Time Relationship

The key insight: **the timer thread uses `wait(tick_period)`**, which advances SystemC simulation time. This means:

- If the timer is configured for 1 MHz (1 µs per tick) and PERIOD = 1000, the IRQ fires every 1 ms of simulation time.
- The CPU model — also running in simulation time — will have executed exactly as many simulated instructions as it would in 1 ms of real hardware time.
- Host speed is irrelevant; correctness depends only on the ratio of simulated frequencies.

## Configuring the Timer from Software

Software interacts via MMIO writes captured by `b_transport`:

```cpp
void VirtualTimer::b_transport(tlm::tlm_generic_payload& trans,
                                sc_time& delay) {
    uint64_t addr   = trans.get_address();
    uint8_t* data   = trans.get_data_ptr();
    bool     is_write = (trans.get_command() == tlm::TLM_WRITE_COMMAND);

    switch (addr) {
        case 0x00: if (is_write) ctrl   = *(uint32_t*)data;
                   else          *(uint32_t*)data = ctrl;   break;
        case 0x04: if (is_write) period = *(uint32_t*)data; break;
        case 0x08: *(uint32_t*)data = counter;              break;  // RO
        case 0x0C: if (is_write) status &= ~(*(uint32_t*)data);     // W1C
                   else          *(uint32_t*)data = status; break;
    }
    trans.set_response_status(tlm::TLM_OK_RESPONSE);
}
```

## One-Shot vs Periodic Mode

| Mode | Counter Behavior | When Interrupt Fires |
|---|---|---|
| One-shot | Stops at PERIOD | Once; must be re-enabled by SW |
| Periodic | Resets to 0 at PERIOD | Repeatedly every PERIOD ticks |

## Common Pitfalls

- **Using `wait(0, SC_NS)`:** This creates a zero-time wait which may starve other processes. Always use a real tick period.
- **Reading counter mid-tick:** The counter value changes only at tick boundaries. If software reads it between waits it sees the last committed value — this is actually correct behavior.
- **Forgetting Status W1C:** The status "write-1-to-clear" (W1C) pattern is essential. If software cannot clear the status bit, the ISR runs in an infinite loop.
- **Tick period too coarse:** A tick period of 1 µs is fine for millisecond-range timers. For sub-microsecond events, choose a smaller tick period and accept longer simulation time.

> **Interview answer:** A virtual timer uses an `SC_THREAD` that calls `wait(tick_period)` in a loop to advance SystemC simulation time. Each tick increments a counter; when it reaches the period register, the model asserts an IRQ output and optionally resets the counter for periodic operation — all driven by simulation time, not host wall-clock time.
