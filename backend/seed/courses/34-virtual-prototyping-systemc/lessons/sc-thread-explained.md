# SC_THREAD: Suspendable Processes

`SC_THREAD` is the process type that can **suspend itself mid-execution** and resume later. This makes it possible to write sequential behaviours — protocols, state machines, bus transactions — as straight-line C++ rather than as a chain of callbacks.

## The Key Difference

An `SC_METHOD` returns control to the kernel the moment its function returns. An `SC_THREAD` keeps its **call stack alive** between activations, so local variables and the program counter are preserved across `wait()` calls.

Under the hood, most SystemC implementations realise threads as **green threads / coroutines** (not OS threads), so there is still only one thread of execution at a time — the kernel switches between them cooperatively.

## Registration

```cpp
SC_MODULE(UartTx) {
    sc_in<bool>         clk;
    sc_in<sc_uint<8>>  data;
    sc_in<bool>         valid;
    sc_out<bool>        tx;

    SC_CTOR(UartTx) {
        SC_THREAD(transmit);
        sensitive << clk.pos();   // initial sensitivity (can be overridden by wait())
    }

    void transmit();
};
```

## Anatomy of a Thread Body

```cpp
void UartTx::transmit() {
    tx.write(1);           // idle line high

    while (true) {
        wait();            // suspend until next positive clock edge

        if (!valid.read()) continue;

        // Start bit
        tx.write(0);
        wait();            // one clock period

        // Data bits (LSB first)
        for (int i = 0; i < 8; i++) {
            tx.write((data.read() >> i) & 1);
            wait();
        }

        // Stop bit
        tx.write(1);
        wait();
    }
}
```

Key observations:

- The `while(true)` loop is legal because `wait()` suspends the thread between iterations.
- Local variable `i` is preserved across each `wait()` call — the stack is saved.
- The thread never returns; this is the expected pattern for hardware processes.

## Forms of wait()

Inside `SC_THREAD`, `wait()` can take several forms:

| Call | Suspends until... |
|---|---|
| `wait()` | Next event on static sensitivity list |
| `wait(sig.value_changed_event())` | Specific event |
| `wait(10, SC_NS)` | 10 nanoseconds of simulation time |
| `wait(10, SC_NS, sig.value_changed_event())` | Timeout OR event |
| `wait(3)` | Static sensitivity fires 3 times |

## Thread Lifecycle

```
sc_start() called
  └─► Thread body begins at first statement
        │
       wait() ──► kernel runs other processes
        │
      event fires ──► thread resumes at next statement after wait()
        │
      ... (repeats) ...
        │
      Thread function returns or sc_stop() called ──► thread terminates
```

Once an `SC_THREAD` terminates (its function returns), it **cannot be restarted**. In hardware models, threads almost always contain an infinite loop for this reason.

## Why SC_THREAD is Powerful for Protocol Modelling

Consider an I2C start condition: pull SDA low, then pull SCL low. Expressing this with `SC_METHOD` requires breaking the sequence into multiple callback states. With `SC_THREAD`:

```cpp
void i2c_start() {
    sda.write(0);
    wait(5, SC_NS);    // SDA low for setup time
    scl.write(0);
    wait(5, SC_NS);    // SCL low
}
```

The code reads exactly like the timing diagram — making it far easier to verify against a protocol specification.

## Common Pitfall: Calling wait() Without Sensitivity

An `SC_THREAD` that calls `wait()` without a static sensitivity list and without passing an event to `wait()` will **hang forever**:

```cpp
SC_CTOR(Foo) {
    SC_THREAD(run);
    // forgot: sensitive << clk.pos();
}

void run() {
    while (true) {
        wait();   // waits for... nothing. Simulation deadlock.
    }
}
```

Always ensure either a static sensitivity list exists or every `wait()` call specifies an event or timeout.

> **Interview answer:** `SC_THREAD` is a suspendable process that preserves its call stack across `wait()` calls, enabling sequential protocol logic to be written as straight-line C++. It runs in an infinite loop and is driven by clock edges or events, making it ideal for FSMs, bus transactions, and anything with multi-cycle behaviour.
