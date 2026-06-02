# Quiz: TLM-2.0 Fundamentals

Test your understanding of TLM-2.0 sockets, the generic payload, transport interfaces, DMI, extensions, and the interoperability layer.

---

**Q1. Which TLM-2.0 transport function models a complete bus transaction as a single C++ function call, returning only after the transaction is finished?**

- [ ] `nb_transport_fw`
- [x] `b_transport`
- [ ] `transport_dbg`
- [ ] `get_direct_mem_ptr`

`b_transport` is the blocking (LT) transport; it returns only when the transaction is done. `nb_transport_fw` returns immediately with a sync enum and completes asynchronously.

---

**Q2. In the TLM-2.0 generic payload, what should an initiator set `response_status` to BEFORE calling `b_transport`?**

- [ ] `TLM_OK_RESPONSE`
- [ ] `TLM_GENERIC_ERROR_RESPONSE`
- [x] `TLM_INCOMPLETE_RESPONSE`
- [ ] `TLM_ADDRESS_ERROR_RESPONSE`

`TLM_INCOMPLETE_RESPONSE` is the sentinel value that signals "not yet answered". After the call returns, the initiator checks whether the target replaced it with `TLM_OK_RESPONSE` or an error code.

---

**Q3. What is the primary purpose of the Direct Memory Interface (DMI) in TLM-2.0?**

- [ ] To allow a target to call back the initiator asynchronously
- [ ] To provide a non-destructive inspection channel for debuggers
- [ ] To encode burst type and QoS priority in a transaction
- [x] To expose a raw C++ pointer to the target's backing memory, eliminating socket overhead for repeated accesses

DMI hands a pointer covering an address range to the initiator so subsequent accesses use `memcpy` instead of going through the socket, yielding 5-20x speed improvements for instruction-fetch-heavy workloads.

---

**Q4. A target receives a `tlm_generic_payload` with an extension it has never seen before. What should it do according to TLM-2.0 interoperability rules?**

- [ ] Abort the simulation with an error
- [ ] Return `TLM_COMMAND_ERROR_RESPONSE` immediately
- [x] Check for the extension with `get_extension()`, find `nullptr`, and proceed with a default behavior
- [ ] Clone the extension and forward it to the next target unchanged

Extensions are optional by definition. A compliant target calls `get_extension<T>()`, checks for null, and falls back gracefully — this is the rule that keeps TLM-2.0 models interoperable across projects.

---

**Q5. In the Approximately-Timed (AT) style, which sequence of phases correctly represents a full read transaction handshake?**

- [ ] `BEGIN_REQ` → `BEGIN_RESP` → `END_REQ` → `END_RESP`
- [ ] `BEGIN_REQ` → `END_RESP` → `BEGIN_RESP` → `END_REQ`
- [x] `BEGIN_REQ` → `END_REQ` → `BEGIN_RESP` → `END_RESP`
- [ ] `END_REQ` → `BEGIN_REQ` → `END_RESP` → `BEGIN_RESP`

The standard four-phase handshake is: initiator sends `BEGIN_REQ`, target acknowledges with `END_REQ` (address sampled), target sends `BEGIN_RESP` (data valid), initiator closes with `END_RESP`.

---

**Q6. Which `tlm_utils` convenience socket class should you use when one bus target needs to accept connections from multiple initiators, distinguishing each caller by an integer `id`?**

- [ ] `simple_target_socket`
- [ ] `simple_initiator_socket`
- [ ] `multi_passthrough_initiator_socket`
- [x] `multi_passthrough_target_socket`

`multi_passthrough_target_socket` accepts N bindings from different initiators and passes an integer `id` parameter to each registered callback so the target can identify which master originated the transaction.
