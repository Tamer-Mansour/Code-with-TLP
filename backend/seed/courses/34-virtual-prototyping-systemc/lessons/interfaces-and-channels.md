# Interfaces, Channels, and Ports

The SystemC communication model is built on a clean separation of *what* a channel can do (interface), *how* it does it (channel), and *who uses it* (port). Understanding this trio is essential for writing reusable, composable models.

## The Three-Layer Model

```
┌──────────────┐          ┌──────────────────────────┐
│    Module    │          │         Channel           │
│              │          │  (implements IF)          │
│  sc_port<IF> │──────────▶  sc_signal<T>             │
│              │          │  sc_fifo<T>               │
│              │          │  sc_mutex                 │
└──────────────┘          └──────────────────────────┘
        ▲                            ▲
        │                            │
   declares need              inherits from IF
```

### Interface

An **interface** is a pure-virtual C++ class derived from `sc_interface`. It defines the *contract* — the set of methods a channel must implement.

```cpp
// Simplified view of sc_signal_in_if<T>
template<class T>
class sc_signal_in_if : public sc_interface {
public:
    virtual const T& read() const = 0;
    virtual const sc_event& value_changed_event() const = 0;
    virtual bool event() const = 0;
};
```

You can define custom interfaces for domain-specific protocols:

```cpp
class write_if : public sc_interface {
public:
    virtual void write(int data) = 0;
};
```

### Channel

A **channel** implements one or more interfaces and encapsulates the communication behavior. It must inherit from `sc_prim_channel` (primitive) or `sc_channel` (hierarchical).

```cpp
class my_fifo : public sc_prim_channel,
                public sc_fifo_in_if<int>,
                public sc_fifo_out_if<int> {
    // ...full protocol implementation...
};
```

### Port

A **port** (`sc_port<IF>`) is the module's socket. It forwards calls to the bound channel:

```cpp
SC_MODULE(Consumer) {
    sc_port<sc_fifo_in_if<int>> in_port;

    void run() {
        int val = in_port->read();  // -> forwards to channel's read()
    }
};
```

## Standard SystemC Channels

| Channel | Interface(s) | Typical Use |
|---|---|---|
| `sc_signal<T>` | `sc_signal_in_if`, `sc_signal_inout_if` | RTL wire |
| `sc_fifo<T>` | `sc_fifo_in_if`, `sc_fifo_out_if` | Buffered data stream |
| `sc_mutex` | `sc_mutex_if` | Mutual exclusion |
| `sc_semaphore` | `sc_semaphore_if` | Resource counting |
| `sc_buffer<T>` | Same as sc_signal | Notifies on every write |

## Custom Channel Example

```cpp
// Interface
class timer_if : public sc_interface {
public:
    virtual void start(sc_time duration) = 0;
    virtual const sc_event& expired() const = 0;
};

// Channel
class timer_channel : public sc_prim_channel, public timer_if {
    sc_event exp_event;
public:
    void start(sc_time d) override {
        exp_event.notify(d);   // fire after delay
    }
    const sc_event& expired() const override { return exp_event; }
};

// Module using the channel
SC_MODULE(Watchdog) {
    sc_port<timer_if> tmr;

    SC_CTOR(Watchdog) {
        SC_THREAD(monitor);
    }
    void monitor() {
        tmr->start(sc_time(5, SC_MS));
        wait(tmr->expired());
        std::cout << "Timeout!\n";
    }
};
```

## Key Design Rules

1. **Interfaces are immutable contracts**: once published, adding a virtual method breaks all existing implementations.
2. **Channels own their events**: events returned from an interface method must live as long as the channel.
3. **Ports bind at elaboration**: all bindings must be complete before `sc_start()` is called.
4. **One port, one interface, many channels**: a single port can only be bound to one channel instance (unless multiplicity > 1 is specified).

## Common Pitfalls

- **Forgetting `sc_interface` base**: if your custom interface does not inherit from `sc_interface`, `sc_port` will reject it at compile time.
- **Calling channel methods in constructors**: channels are not yet bound; call them only from `before_end_of_elaboration()` or simulation processes.
- **Returning local events**: events must be members of the channel, not local variables — dangling reference danger.

> **Interview answer:** In SystemC, an interface declares the protocol as pure-virtual methods, a channel implements those methods and owns the communication state, and a port is the module-side proxy that forwards calls to the bound channel — this three-layer pattern enables loose coupling and channel substitutability.
