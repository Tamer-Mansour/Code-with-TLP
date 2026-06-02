# Modeling State Machines with Processes

Finite State Machines (FSMs) are everywhere in digital hardware — bus controllers, protocol engines, arbiters, and sequencers are all FSMs. SystemC offers two clean styles: the **enum + switch SC_METHOD** and the **structured SC_THREAD** approach.

## The Two FSM Styles

### Style 1: SC_METHOD with Explicit State Variable

This mirrors how Verilog `always` blocks model FSMs. The state is stored in a module-level variable; the method reads the state and transitions it.

```cpp
SC_MODULE(TrafficLight) {
    sc_in<bool>  clk;
    sc_in<bool>  sensor;  // car detected
    sc_out<uint8_t> light; // 0=RED 1=GREEN 2=YELLOW

    enum State { RED, GREEN, YELLOW };
    State current_state;
    int   timer;

    SC_CTOR(TrafficLight) : current_state(RED), timer(0) {
        SC_METHOD(fsm_proc);
        sensitive << clk.pos();
    }

    void fsm_proc() {
        switch (current_state) {
            case RED:
                light.write(0);
                if (++timer >= 30) { timer = 0; current_state = GREEN; }
                break;
            case GREEN:
                light.write(1);
                if (!sensor.read() || ++timer >= 60) {
                    timer = 0; current_state = YELLOW;
                }
                break;
            case YELLOW:
                light.write(2);
                if (++timer >= 5) { timer = 0; current_state = RED; }
                break;
        }
    }
};
```

- The method fires every clock cycle.
- State transitions happen at the end of `fsm_proc`.
- Works well for synthesis; every state is explicit.

### Style 2: SC_THREAD with Structured Control Flow

The same FSM as straight-line code with `wait()`:

```cpp
void TrafficLight::fsm_proc() {
    while (true) {
        // RED state
        light.write(0);
        for (int i = 0; i < 30; i++) wait();

        // GREEN state
        light.write(1);
        int t = 0;
        do { wait(); t++; } while (sensor.read() && t < 60);

        // YELLOW state
        light.write(2);
        for (int i = 0; i < 5; i++) wait();
    }
}
```

No enum, no switch, no timer variable — the call stack *is* the state. This is dramatically more readable for complex FSMs.

## Comparison Table

| Aspect | SC_METHOD + enum | SC_THREAD |
|---|---|---|
| Code readability | Moderate | High |
| Explicit state variable | Required | Not needed |
| Synthesisable as-is | Yes (with HLS) | Only with SC_CTHREAD |
| Simulation overhead | Lower | Slightly higher |
| Nested/hierarchical states | Verbose | Easy (function calls) |
| Debugging | Step through enum | Step through lines |

## Hierarchical State Machines

`SC_THREAD` makes hierarchical FSMs natural using **helper functions**:

```cpp
void usb_controller() {
    while (true) {
        wait_for_connect();     // sub-state machine as function
        enumerate_device();
        transfer_data();
        handle_disconnect();
    }
}

void wait_for_connect() {
    while (!vbus.read()) wait();  // spin until VBUS detected
    wait(100, SC_MS);             // debounce
}
```

Each helper function can contain its own loops and `wait()` calls. Implementing this cleanly with `SC_METHOD` would require a two-level enum.

## Mealy vs Moore Outputs

- **Moore FSM** — output depends only on current state: compute output at the top of each state block.
- **Mealy FSM** — output depends on state AND input: compute output inline with input reads.

```cpp
// Moore: output set when entering state
light.write(GREEN_VALUE);
for (int i = 0; i < GREEN_CYCLES; i++) wait();

// Mealy: output depends on input observed while in state
while (state == ARBITRATE) {
    grant.write(req_a.read() ? 1 : (req_b.read() ? 2 : 0));
    wait();
}
```

## Reset Pattern

Always handle reset explicitly in state machine threads:

```cpp
void fsm_thread() {
    // Reset actions
    state_out.write(IDLE);
    grant.write(0);
    wait();               // let reset propagate

    while (true) {
        // Normal operation FSM
        ...
    }
}
```

Use `SC_CTHREAD` with `reset_signal_is()` for automatic reset restart when targeting synthesis.

## Common Pitfall: Missing a wait() in a State

A state that loops without `wait()` spins **forever** — the kernel never advances time and the simulation hangs:

```cpp
// DEADLOCK: no wait() inside the loop
while (!grant.read()) { /* busy-wait — never yields! */ }

// CORRECT:
while (!grant.read()) wait();
```

> **Interview answer:** SystemC FSMs can be modelled with either an SC_METHOD holding an explicit state enum (mirrors RTL always blocks, synthesis-friendly) or an SC_THREAD where the program counter IS the state (more readable, ideal for complex multi-cycle protocols). SC_THREAD avoids explicit state variables but requires every state to contain at least one wait() call.
