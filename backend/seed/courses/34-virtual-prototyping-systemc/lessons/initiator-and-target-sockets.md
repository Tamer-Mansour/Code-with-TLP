# Initiator and Target Sockets

Sockets are the connectors of TLM-2.0. They bundle a transport interface, a binding mechanism, and a protocol type into a single strongly-typed object. Instead of declaring separate ports and exports and then binding them individually, you declare one socket and let the TLM-2.0 infrastructure wire everything up.

## Socket Types at a Glance

| Socket Class | Direction | Typical Location |
|---|---|---|
| `tlm_initiator_socket<BUSWIDTH>` | Sends transactions | CPU, DMA master |
| `tlm_target_socket<BUSWIDTH>` | Receives transactions | Memory, peripheral |
| `tlm_base_initiator_socket` | Un-parameterized base | Adapters, analyzers |
| `tlm_base_target_socket` | Un-parameterized base | Adapters, analyzers |

The default bus width is 32 bits. Pass a different width as the template parameter when modeling a 64-bit AXI bus or an 8-bit serial link.

## Declaring Sockets in a Module

```cpp
#include "tlm.h"
#include "tlm_utils/simple_initiator_socket.h"
#include "tlm_utils/simple_target_socket.h"

// Initiator (e.g., a CPU model)
struct Cpu : sc_core::sc_module {
    tlm_utils::simple_initiator_socket<Cpu> socket;

    SC_CTOR(Cpu) : socket("socket") {
        SC_THREAD(run);
    }
    void run();
};

// Target (e.g., a RAM model)
struct Ram : sc_core::sc_module {
    tlm_utils::simple_target_socket<Ram> socket;

    SC_CTOR(Ram) : socket("socket") {
        socket.register_b_transport(this, &Ram::b_transport);
    }
    void b_transport(tlm::tlm_generic_payload&, sc_core::sc_time&);
};
```

The `simple_*_socket` helpers from `tlm_utils` are the most common starting point. They automatically implement the transport interface for you so you only need to register callback methods.

## Binding Sockets

Binding uses the familiar `()` operator, mirroring how SystemC ports are connected:

```cpp
SC_MODULE(Top) {
    Cpu  cpu;
    Ram  ram;

    SC_CTOR(Top) : cpu("cpu"), ram("ram") {
        cpu.socket.bind(ram.socket);  // initiator -> target
    }
};
```

For more complex topologies (crossbars, buses) you can chain multiple sockets through a component that passes transactions along. Multi-passthrough sockets (`tlm_utils::multi_passthrough_initiator_socket`) let one target accept connections from several initiators, assigning each a unique `id` in the callback.

## The Transport Interface Contract

When you bind an initiator socket to a target socket, the initiator gains access to these functions on the target:

```cpp
// Blocking transport (LT style)
virtual void b_transport(tlm_generic_payload& trans,
                         sc_core::sc_time& t) = 0;

// Non-blocking forward path (AT style)
virtual tlm_sync_enum nb_transport_fw(tlm_generic_payload& trans,
                                      tlm_phase& phase,
                                      sc_core::sc_time& t) = 0;

// DMI hint
virtual bool get_direct_mem_ptr(tlm_generic_payload& trans,
                                tlm_dmi& dmi_data) = 0;

// Debug transport
virtual unsigned int transport_dbg(tlm_generic_payload& trans) = 0;
```

A target is not required to implement all four, but a socket that claims interoperability must at minimum provide `b_transport` (for LT) or `nb_transport_fw` (for AT).

## Hierarchical Binding

Sometimes a socket lives inside a sub-module but needs to be exposed at the parent boundary. TLM-2.0 supports hierarchical passthrough binding:

```cpp
// Inside a wrapper module that exposes its child's socket
SC_CTOR(Wrapper) {
    initiator_socket.bind(child.initiator_socket);  // passthrough
}
```

This is the same semantics as binding a regular SystemC port to a child's port — no data copy occurs; the sockets share the same interface object.

## Common Pitfalls

- **Template width mismatch** — binding a `tlm_initiator_socket<32>` to a `tlm_target_socket<64>` is a compile error. Always match widths or use an adapter.
- **Forgetting to register callbacks** — with `simple_target_socket`, if you do not call `register_b_transport` before simulation starts, any incoming transaction will call a null function pointer.
- **Multiple bindings on a plain socket** — `tlm_initiator_socket` accepts exactly one binding. Use `multi_passthrough_initiator_socket` when one master talks to many slaves.

> **Interview answer:** TLM-2.0 initiator sockets represent bus masters and target sockets represent bus slaves; binding them with `socket.bind(target.socket)` wires the full transport interface (b_transport, nb_transport, DMI, debug) between the two modules in a type-safe, width-checked way.
