# Modeling Latency and Bandwidth

Latency and bandwidth are the two numbers that determine how fast a system actually runs. Getting them right in your virtual prototype means software timing measurements match silicon — close enough to profile, tune, and catch bottlenecks before tape-out.

## Key Definitions

| Term | Formula | Unit |
|------|---------|------|
| **Latency** | Time from transaction issue to completion | ns / cycles |
| **Bandwidth** | Maximum data rate of the bus | GB/s |
| **Throughput** | Actual achieved data rate under load | GB/s |
| **Utilization** | Throughput / Bandwidth | % |

Latency and bandwidth are independent constraints. A bus can have low latency but low bandwidth (narrow data path), or high bandwidth but high latency (deep pipeline).

## Latency Components

A real bus transaction accumulates latency from multiple sources:

```
Total latency = arbitration_wait
              + address_decode
              + bus_pipeline_stages × clk_period
              + target_access_time
              + response_propagation
```

In TLM-2.0, all of these are accumulated in the `sc_time& delay` parameter passed through `b_transport()`:

```cpp
void b_transport(tlm::tlm_generic_payload& txn, sc_time& delay) {
    // 1. Arbitration (if lock was contested)
    delay += sc_time(ARB_LATENCY_NS, SC_NS);

    // 2. Decode + pipeline
    delay += sc_time(BUS_PIPELINE_NS, SC_NS);

    // 3. Forward to target (target adds its own access time)
    target_socket[idx]->b_transport(txn, delay);

    // 4. Response pipeline (read data path)
    if (txn.get_command() == tlm::TLM_READ_COMMAND)
        delay += sc_time(RESP_PIPELINE_NS, SC_NS);
}
```

## Bandwidth Modeling

Bandwidth depends on bus width (bytes per beat) and clock frequency. For a burst transaction:

```
bandwidth_limit = (bus_width_bytes × clk_freq_hz)   [bytes/s]
burst_time      = burst_length_bytes / bandwidth_limit
```

Model bandwidth by adding the burst transfer time to the delay:

```cpp
const double BUS_WIDTH_BYTES = 8;     // 64-bit bus
const double CLK_FREQ_HZ     = 1e9;  // 1 GHz

void add_bandwidth_delay(tlm::tlm_generic_payload& txn,
                         sc_time& delay) {
    uint32_t bytes = txn.get_data_length();
    double   ns    = (bytes / BUS_WIDTH_BYTES) / CLK_FREQ_HZ * 1e9;
    delay += sc_time(ns, SC_NS);
}
```

## Approximate Timing vs. Cycle-Accurate

| Approach | Delay model | Simulation speed | Accuracy |
|----------|-------------|-----------------|----------|
| Loosely Timed (LT) | Accumulated in `delay`, flushed at `wait()` | Fastest | ±10-20% |
| Approximately Timed (AT) | `wait(delay)` inside bus model | Moderate | ±1-5% |
| Cycle-accurate TLM | Explicit clock edge tracking | Slow | <1% |

For software bring-up, use LT. For performance analysis with profiling, use AT. Cycle-accurate is rarely needed above IP-block level.

## Bandwidth Saturation

When multiple initiators hammer the bus, total throughput hits the bandwidth ceiling. Model saturation by tracking a shared **credit counter**:

```cpp
int bandwidth_credits_ = MAX_CREDITS; // resets each sim cycle

void b_transport(...) {
    int cost = txn.get_data_length() / BUS_WIDTH_BYTES;
    if (bandwidth_credits_ < cost) {
        // Stall: add wait time for next refill
        delay += CLK_PERIOD;
        bandwidth_credits_ = MAX_CREDITS;
    }
    bandwidth_credits_ -= cost;
    // ... forward transaction
}
```

## Worked Example: DDR Controller Latency

A Cortex-A core issues a 64-byte cache-line fill over AXI to a DDR controller:

```
AXI arbitration:      5 ns   (contested, two masters)
AXI address decode:   1 ns
DDR row open (tRCD):  15 ns
DDR column read (CL): 14 ns
DDR burst transfer:   8 ns   (8 beats × 1 ns each)
AXI return path:      2 ns
─────────────────────────────
Total read latency:   45 ns
```

Model each component as a named constant so tuning one does not silently break another.

## Common Pitfalls

- **Using wall-clock time instead of sc_time**: `std::chrono` has no meaning in simulation; always use `sc_time`.
- **Adding latency on both sides of a bridge**: If the AXI bus and the APB target both add pipeline latency for the same hop, you double-count.
- **Ignoring back-pressure**: A target that is busy must signal `TLM_INCOMPLETE_RESPONSE` or use the AT phase protocol; returning OK instantly is wrong.
- **Fixed latency regardless of burst length**: Bandwidth depends on length — a single-beat and a 16-beat burst must not cost the same.

**Interview answer:** "TLM latency is modeled by accumulating sc_time delays across arbitration, bus pipeline stages, and target access time in the delay parameter of b_transport. Bandwidth is modeled by dividing burst byte count by the bus width times clock frequency, then adding that duration to the delay."
