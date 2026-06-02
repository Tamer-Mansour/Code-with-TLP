# Phases in AT: BEGIN_REQ to END_RESP

The four standard phases of the TLM-2.0 AT protocol define a handshake between initiator and target. Understanding what each phase signifies — and who is responsible for driving it — is essential for writing correct AT models.

## The Four Standard Phases

```
Initiator                              Target
    │                                     │
    │──── nb_transport_fw(BEGIN_REQ) ────►│  "I want to start a transaction"
    │                                     │
    │◄─── nb_transport_bw(END_REQ) ──────│  "I've accepted your request"
    │                                     │
    │◄─── nb_transport_bw(BEGIN_RESP) ───│  "Here is my response"
    │                                     │
    │──── nb_transport_fw(END_RESP) ────►│  "I've received your response"
    │                                     │
```

The arrows represent function calls across the socket pair. `nb_transport_fw` travels from initiator to target; `nb_transport_bw` travels from target to initiator.

## Phase Definitions

### BEGIN_REQ
The initiator drives `BEGIN_REQ` to indicate it wants to issue a transaction. The payload is fully populated (address, command, data pointer for writes). The initiator owns the payload from this point until `END_RESP`.

```cpp
tlm::tlm_phase phase = tlm::BEGIN_REQ;
sc_core::sc_time t   = sc_core::SC_ZERO_TIME;
auto status = socket->nb_transport_fw(trans, phase, t);
```

### END_REQ
The target drives `END_REQ` (via `nb_transport_bw` callback, or by modifying `phase` in the return from `BEGIN_REQ`) to signal that it has accepted the request and the initiator may issue the next one. The initiator must not re-use the payload until this phase.

```cpp
// Target handling BEGIN_REQ — accept and schedule END_REQ
if (phase == tlm::BEGIN_REQ) {
    phase = tlm::END_REQ;
    t     = sc_core::sc_time(5, SC_NS);   // request accepted after 5 ns
    return tlm::TLM_UPDATED;
}
```

### BEGIN_RESP
The target drives `BEGIN_RESP` (via `nb_transport_bw`) to deliver the response. For reads, the data pointer now contains valid read data. The `sc_time` parameter annotates when the response is valid.

```cpp
// Target spawning a thread to send the response later
void send_response_thread() {
    wait(response_event);   // wait for the data to be ready

    tlm::tlm_phase bw_phase = tlm::BEGIN_RESP;
    sc_core::sc_time t      = sc_core::SC_ZERO_TIME;
    bw_socket->nb_transport_bw(*pending_trans, bw_phase, t);
}
```

### END_RESP
The initiator drives `END_RESP` (via `nb_transport_fw`) to acknowledge that it has consumed the response. After this, the target may release any reference to the payload. This is the final phase; the transaction is complete.

```cpp
// Initiator handling BEGIN_RESP callback — acknowledge
tlm::tlm_sync_enum nb_transport_bw(tlm::tlm_generic_payload& trans,
                                   tlm::tlm_phase& phase,
                                   sc_core::sc_time& t) {
    if (phase == tlm::BEGIN_RESP) {
        // Consume the response data
        phase = tlm::END_RESP;
        t     = sc_core::SC_ZERO_TIME;
        socket->nb_transport_fw(trans, phase, t);
        response_received_event.notify();
        return tlm::TLM_COMPLETED;
    }
    return tlm::TLM_ACCEPTED;
}
```

## Timing Along the Protocol

Each phase call carries an `sc_time& t` parameter that annotates the *additional delay* relative to the current simulation time at which the event occurs. This is not a timestamp; it is an offset.

```
Global time = 100 ns

nb_transport_fw(BEGIN_REQ, t=0 ns)   → request issued at 100 ns
nb_transport_bw(END_REQ,   t=5 ns)   → request accepted at 105 ns
nb_transport_bw(BEGIN_RESP,t=20 ns)  → response ready at 120 ns
nb_transport_fw(END_RESP,  t=0 ns)   → acknowledged at 120 ns
```

## Collapsed Protocol

Not every transaction needs all four phases. A fast target can return `TLM_COMPLETED` from `BEGIN_REQ` with `phase` set to `END_RESP`, skipping the intermediate steps. This "collapsed" AT protocol delivers a response in one function call, identical to LT performance but using the non-blocking interface.

## Protocol Violations to Avoid

| Violation | Consequence |
|---|---|
| Initiator reuses payload before `END_REQ` | Data corruption in pipelined bus |
| Target holds `END_REQ` indefinitely | Initiator stalls; no new requests possible |
| Initiator never sends `END_RESP` | Target's payload pointer leaks; memory grows |
| Sending `BEGIN_RESP` before `END_REQ` | Protocol ordering violation; undefined behavior |

> **Interview answer:** "AT has four standard phases: BEGIN_REQ (initiator starts a transaction), END_REQ (target accepts the request), BEGIN_RESP (target delivers the response), and END_RESP (initiator acknowledges). Each phase is a function call on the nb_transport interface and carries an annotated time delay."
