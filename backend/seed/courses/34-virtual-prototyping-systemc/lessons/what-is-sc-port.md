# What Is sc_port?

`sc_port<IF>` is SystemC's typed connection point that binds a module to a channel implementing interface `IF`. A port is not a value container — it is a *proxy* that forwards method calls to whatever channel is bound to it at elaboration time.

## The Port-Interface-Channel Triangle

SystemC communication rests on three collaborating entities:

```
Module A          Module B
  |                  |
sc_port<IF>      sc_port<IF>
       \            /
        sc_signal<T>    <-- channel that implements IF
```

- **Interface (`IF`)**: a pure-virtual C++ class declaring the protocol methods (`read`, `write`, `posedge_event`, …).
- **Channel**: a concrete class implementing `IF` (e.g., `sc_signal<bool>` implements `sc_signal_in_if<bool>`).
- **Port**: an `sc_port<IF>` bound to a channel; calls on the port are forwarded to the channel.

## Directional Helpers

SystemC provides convenience typedefs so you rarely write raw `sc_port<>` in RTL-style modeling:

| Typedef | Underlying Port |
|---|---|
| `sc_in<T>` | `sc_port<sc_signal_in_if<T>>` |
| `sc_out<T>` | `sc_port<sc_signal_inout_if<T>>` |
| `sc_inout<T>` | `sc_port<sc_signal_inout_if<T>>` |

## Declaring Ports

```cpp
SC_MODULE(Adder) {
    sc_in<sc_uint<8>>  a, b;   // input ports
    sc_out<sc_uint<9>> sum;    // output port

    SC_CTOR(Adder) {
        SC_METHOD(compute);
        sensitive << a << b;
    }

    void compute() {
        sum.write(a.read() + b.read());
    }
};
```

## Binding Ports to Channels

Binding happens in the parent module's constructor (elaboration phase):

```cpp
SC_MODULE(Top) {
    sc_signal<sc_uint<8>>  sig_a, sig_b;
    sc_signal<sc_uint<9>>  sig_sum;
    Adder adder;

    SC_CTOR(Top) : adder("adder") {
        adder.a(sig_a);       // bind port to channel
        adder.b(sig_b);
        adder.sum(sig_sum);
    }
};
```

Ports can also be bound port-to-port when hierarchically composing modules:

```cpp
// Inside a wrapper module
child.a(this->a);  // outer port binds to inner port
```

## Port Multiplicity

By default `sc_port<IF>` accepts exactly one binding. Pass a second template argument to allow multiple bindings (useful for bus masters):

```cpp
sc_port<sc_signal_in_if<bool>, 4>  bus_lines;  // expects 4 bindings
sc_port<sc_signal_in_if<bool>, 0>  any_lines;  // 0 = unbounded
```

## Common Pitfalls

1. **Unbound port at simulation start**: SystemC will throw an error. Every declared port must be connected before `sc_start()`.
2. **Writing through an `sc_in` port**: `sc_in<T>` only exposes `read()` — attempting `write()` is a compile error, which is the desired protection.
3. **Port-to-port binding direction**: binding an inner `sc_out` to an outer `sc_in` is a type mismatch detected at compile time.

## Why Ports Exist

Ports decouple the module's *protocol requirements* from the concrete channel implementation. You can swap `sc_signal<bool>` for a custom FIFO channel without touching the module, as long as the channel implements the same interface.

> **Interview answer:** `sc_port<IF>` is a typed proxy that a module declares to express its communication requirements; it delegates all calls to the concrete channel bound during elaboration, enabling loose coupling between modules and channels.
