# SystemC, IEEE 1666, and TLM-2.0

SystemC did not emerge fully-formed as an IEEE standard — it evolved through industry collaboration over a decade. Understanding this history explains why certain APIs exist, why TLM-2.0 is a separate but related specification, and how to read documentation that references different versions.

## The Timeline

| Year | Event |
|------|-------|
| 1999 | Synopsys and CoWare release SystemC 1.0 as open source |
| 2000 | Open SystemC Initiative (OSCI) formed; SystemC 2.0 released |
| 2002 | SystemC 2.0.1 — refined simulation semantics |
| 2005 | SystemC 2.1 + TLM-1.0 (first transaction-level modeling standard) |
| 2008 | SystemC 2.2 + **TLM-2.0** (the modern standard; backward-compatible sockets) |
| 2011 | **IEEE 1666-2011** — SystemC 2.3 ratified as an IEEE standard |
| 2016 | IEEE 1666-2016 — minor clarifications and C++11 alignment |
| 2023 | IEEE 1666-2023 draft — ongoing C++17 alignment and CCI extensions |
| Ongoing | Accellera maintains the open-source reference implementation |

## OSCI to Accellera

The Open SystemC Initiative (OSCI) merged into **Accellera Systems Initiative** in 2012. Accellera now maintains:
- The IEEE 1666 SystemC standard.
- The SystemC reference implementation (Apache 2.0 licensed).
- Additional standards: UVM, IP-XACT, and others.

The GitHub repository `accellera-official/systemc` is the authoritative open-source implementation.

## IEEE 1666-2011 — What It Standardized

Before 1666-2011, SystemC was a de-facto standard governed by OSCI releases. The 2011 IEEE ratification:

- Formally defined module, process, port, and signal semantics.
- Added `sc_vector` for arrays of modules and ports.
- Standardized `sc_report` / `sc_report_handler` for portable error reporting.
- Incorporated `before_end_of_elaboration`, `end_of_elaboration`, `start_of_simulation`, `end_of_simulation` phase callbacks.
- Defined the behavior of `sc_pause()` and `sc_start()` resumption.

## TLM-2.0 — The Transaction-Level Modeling Standard

TLM-2.0 is technically a separate standard (also maintained by Accellera/IEEE 1666-2011 Annex), but it is universally bundled with SystemC 2.2+. It defines:

- **Generic payload** (`tlm_generic_payload`) — a standardized transaction object for memory-mapped bus transfers.
- **Blocking / Non-blocking transport interfaces** — `b_transport`, `nb_transport_fw`, `nb_transport_bw`.
- **Initiator and target sockets** — `tlm_initiator_socket`, `tlm_target_socket` with automatic binding.
- **Timing annotation** — how to attach timing information to transactions without forcing cycle accuracy.
- **Base protocol** — a contract that compliant models must honor, enabling interoperability between IPs from different vendors.

```cpp
// TLM-2.0 blocking transport call (initiator side)
tlm::tlm_generic_payload trans;
sc_time delay = SC_ZERO_TIME;

trans.set_command(tlm::TLM_WRITE_COMMAND);
trans.set_address(0x1000);
trans.set_data_ptr(reinterpret_cast<unsigned char*>(&data));
trans.set_data_length(4);

socket->b_transport(trans, delay);   // blocks until target responds
```

## Why TLM-2.0 Matters More Than RTL SystemC

In practice, the majority of SystemC usage in the industry today is TLM-2.0 virtual platforms:

- ARM ships **Fast Models** as TLM-2.0 targets.
- RISC-V reference platforms (e.g., QEMU-SystemC bridges) expose TLM sockets.
- EDA vendors (Synopsys VDK, Cadence Palladium) consume TLM-2.0 models.
- Automotive AUTOSAR virtual ECU platforms use TLM-2.0 bus fabrics.

RTL-level SystemC is used for synthesis (Catapult HLS, Stratus HLS) but is a distinct and narrower application.

## Practical Version Notes

When you see version numbers in code or documentation:

- `SYSTEMC_VERSION` macro — numeric, e.g., `20181013` (date-based in newer releases).
- `#include <tlm>` or `#include <tlm.h>` — TLM-2.0 headers, separate from `systemc.h`.
- IEEE 1666-2011 compliance is the minimum bar for production use; avoid pre-2008 tutorials that use deprecated OSCI-era APIs.

## Common Pitfalls

- **Referencing OSCI-era tutorials** — some online resources still show `SC_HAS_PROCESS` and hand-written sensitivity lists from SystemC 1.x; prefer IEEE 1666-2011 style.
- **Confusing TLM-1.0 and TLM-2.0 sockets** — they are incompatible; modern code uses TLM-2.0 exclusively.
- **Assuming TLM-2.0 is part of the C++ standard** — it is not; you must link against SystemC and include TLM headers explicitly.

> **Interview answer:** "SystemC was standardized as IEEE 1666-2011 after evolving through OSCI releases since 1999. TLM-2.0, bundled with SystemC 2.2+, defines a portable transaction-level communication framework with generic payloads and initiator/target sockets that enables interoperability between IPs from different vendors. Most production virtual platforms today are TLM-2.0 based."
