# Dynamic Sensitivity with Events

Dynamic sensitivity allows an `SC_THREAD` (or `SC_CTHREAD`) process to change *which* event it is waiting for at runtime, based on the current simulation state. This enables complex, state-dependent sequencing that cannot be expressed with a fixed static list.

## Static vs Dynamic Compared

```
Static (SC_METHOD):           Dynamic (SC_THREAD):
  - Declared once in ctor       - Declared via wait() calls
  - OR of all listed events     - Can be any event or combination
  - Cannot change               - Changes each time wait() is called
  - Re-runs the whole method    - Resumes from the wait() point
```

## The wait() Family

Inside an `SC_THREAD`, `wait()` suspends the coroutine and optionally specifies what to wait for:

```cpp
// Wait for a specific event
wait(my_event);

// Wait for either of two events (OR)
wait(e1 | e2);

// Wait for both in the same delta (AND)
wait(e1 & e2);

// Wait for a time duration (no event)
wait(10, SC_NS);

// Wait for time OR event (timeout pattern)
wait(10, SC_NS, my_event);

// Wait for next clock edge (in SC_CTHREAD context)
wait();
```

## Why Dynamic Sensitivity Matters

Consider a memory controller that must:
1. Wait for a request signal
2. Wait for the bus to be idle
3. Wait for a grant from an arbiter

With static sensitivity this would require a state machine with a flag variable. With dynamic sensitivity, the sequence reads naturally:

```cpp
void mem_ctrl_thread() {
    while (true) {
        wait(req_event);              // step 1: wait for request
        while (bus_busy.read())
            wait(bus_idle_event);     // step 2: wait for bus idle
        arbiter_port->request();
        wait(grant_event);            // step 3: wait for grant
        do_transfer();
    }
}
```

## Worked Example: Handshake Protocol

```cpp
SC_MODULE(Handshake) {
    sc_in_clk          clk;
    sc_in<bool>         valid, ready;
    sc_out<bool>        ack;
    sc_event            transfer_done;

    SC_CTOR(Handshake) {
        SC_THREAD(sender);
        SC_THREAD(receiver);
    }

    void sender() {
        while (true) {
            wait(clk.posedge_event());      // dynamic: wait for edge
            if (valid.read() && ready.read()) {
                ack.write(true);
                transfer_done.notify(SC_ZERO_TIME);
                wait(clk.posedge_event());
                ack.write(false);
            }
        }
    }

    void receiver() {
        while (true) {
            wait(transfer_done);             // dynamic: wait for event
            std::cout << "Transfer at " << sc_time_stamp() << "\n";
        }
    }
};
```

## Timeout Pattern

The two-argument form of `wait()` is invaluable for detecting hung transactions:

```cpp
void watchdog_thread() {
    while (true) {
        wait(TIMEOUT, SC_NS, response_event);
        if (response_event.triggered()) {    // check which woke us
            handle_response();
        } else {
            report_timeout();
        }
    }
}
```

`sc_event::triggered()` returns `true` if the event fired in the current delta cycle — use it to distinguish timeout from event wake-up.

## Dynamic Sensitivity with SC_METHOD

`SC_METHOD` processes cannot call `wait()`. However, a method can use `next_trigger()` to replace its static sensitivity *for the next activation only*:

```cpp
SC_METHOD(state_machine);
sensitive << clk.pos();          // default sensitivity

void state_machine() {
    if (state == IDLE) {
        next_trigger(start_event); // override: next wake is start_event
    } else {
        next_trigger(clk.posedge_event()); // back to clock
    }
}
```

This is the `SC_METHOD` equivalent of dynamic sensitivity.

## Common Pitfalls

1. **Forgetting `while(true)` in SC_THREAD**: a thread that falls off the end of its function causes a simulation error.
2. **Calling `wait()` in SC_METHOD**: this is illegal and throws a runtime exception.
3. **Race between notify and wait**: if `notify()` is called before the thread reaches `wait()`, the notification is lost (no queuing). Use a flag + event or `sc_event_queue` if ordering is uncertain.
4. **Event combinators copy semantics**: `e1 | e2` creates a temporary `sc_event_or_list`; do not store it in a variable across `wait()` calls.

> **Interview answer:** Dynamic sensitivity in SystemC is achieved via `wait(event)` calls inside `SC_THREAD` processes, allowing the process to change what it is waiting for on every suspension, enabling natural sequential description of complex communication protocols.
