# Bus Bridges and Protocol Conversion

A **bus bridge** connects two buses that run different protocols, different clock domains, or different data widths. Bridges are ubiquitous in SoCs: an AXI-to-APB bridge sits between the high-performance bus fabric and the slow peripheral ring, and a clock-domain-crossing (CDC) bridge sits wherever a bus crosses from one frequency island to another.

## What a Bridge Does

A bridge has two sides:

- **Upstream side** (slave interface): accepts transactions from the faster/higher-level bus.
- **Downstream side** (master interface): issues equivalent transactions on the lower-level bus.

The bridge translates the transaction format, adjusts timing, and handles any width or protocol mismatches.

```
[AXI Initiator] --AXI--> [AXI Slave | Bridge | APB Master] --APB--> [Peripheral]
```

## TLM Model of an AXI-to-APB Bridge

In TLM-2.0, a bridge is just a SystemC module with one target socket (upstream) and one initiator socket (downstream):

```cpp
SC_MODULE(AxiToApbBridge) {
    tlm_utils::simple_target_socket<AxiToApbBridge>    axi_slave;
    tlm_utils::simple_initiator_socket<AxiToApbBridge> apb_master;

    void b_transport(tlm::tlm_generic_payload& txn, sc_time& delay) {
        // AXI burst → split into individual APB accesses
        uint32_t addr   = txn.get_address();
        uint32_t length = txn.get_data_length();
        uint8_t* data   = txn.get_data_ptr();

        for (uint32_t offset = 0; offset < length; offset += 4) {
            tlm::tlm_generic_payload apb_txn;
            apb_txn.set_command(txn.get_command());
            apb_txn.set_address(addr + offset);
            apb_txn.set_data_ptr(data + offset);
            apb_txn.set_data_length(4);  // APB is 32-bit

            sc_time apb_delay = SC_ZERO_TIME;
            apb_master->b_transport(apb_txn, apb_delay);
            delay += apb_delay;          // accumulate each APB access
        }
        txn.set_response_status(tlm::TLM_OK_RESPONSE);
    }
};
```

## Data Width Conversion

When the upstream bus is 64-bit and the downstream is 32-bit, the bridge must split each beat:

| AXI beat (64-bit) | Two APB accesses (32-bit each) |
|-------------------|-------------------------------|
| bytes [7:0]       | First APB access (low word)   |
| bytes [15:8]      | Second APB access (high word) |

Width-downsizing doubles the number of downstream transactions. This is a key reason why bandwidth across a narrowing bridge is lower than expected.

## Clock-Domain Crossing Bridges

A CDC bridge adds a FIFO between the two clock domains. In simulation this is modeled as extra latency:

```cpp
// Model CDC: add synchronizer latency (2 destination-domain clocks)
const sc_time SYNC_LATENCY = 2 * FAST_CLK_PERIOD + 2 * SLOW_CLK_PERIOD;
delay += SYNC_LATENCY;
```

Real CDC bridges also handle metastability, but in TLM that concern is hidden; only the timing penalty matters.

## Address Translation at Bridges

Bridges often relocate the address space. An upstream address of `0xC000_0000` might map to `0x0000_0000` on the downstream bus. Implement this as a configurable offset:

```cpp
uint64_t upstream_base_ = 0xC000'0000;
uint64_t downstream_base_ = 0x0000'0000;

// Inside b_transport:
uint64_t local = txn.get_address() - upstream_base_ + downstream_base_;
apb_txn.set_address(local);
```

## Common Pitfalls

- **Missing burst splitting**: Forwarding a multi-beat AXI transaction directly to an APB target that only handles single-beat accesses causes an assertion failure or silent data corruption.
- **Accumulating delay only once**: Each downstream APB access adds its own 2-cycle delay. Forget to accumulate and your latency model will be wildly optimistic.
- **Byte-enable translation**: AXI byte enables (WSTRB) must be re-aligned when crossing a width boundary; a 64-bit WSTRB maps to two 32-bit WSTRBs.
- **Response code mismatch**: APB does not have a rich error code. A bridge must map SLVERR back to `TLM_COMMAND_ERROR_RESPONSE` on the AXI side.

**Interview answer:** "A bus bridge is a TLM module with a slave socket on the upstream bus and a master socket on the downstream bus. It splits wide bursts into narrower transactions, translates addresses, and accumulates latency for each downstream access — making the protocol and width differences transparent to the initiator."
