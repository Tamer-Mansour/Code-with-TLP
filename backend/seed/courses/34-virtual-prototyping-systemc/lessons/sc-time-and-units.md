# sc_time and Time Resolution

SystemC represents simulation time through the `sc_time` class. Understanding how `sc_time` works — and how **time resolution** constrains your model — is essential for writing correct, portable simulations.

## The `sc_time` Class

`sc_time` stores a duration as an integer multiple of the current **time resolution**. You construct it by specifying a value and a time unit:

```cpp
sc_time t1(10, SC_NS);     // 10 nanoseconds
sc_time t2(2.5, SC_NS);    // 2.5 ns (rounded to resolution)
sc_time t3 = SC_ZERO_TIME; // convenience constant: 0
sc_time t4(1, SC_PS);      // 1 picosecond
```

### Time Unit Constants

| Constant | Unit |
|---|---|
| `SC_FS` | femtosecond |
| `SC_PS` | picosecond |
| `SC_NS` | nanosecond |
| `SC_US` | microsecond |
| `SC_MS` | millisecond |
| `SC_SEC` | second |

## Time Resolution

The **time resolution** is the smallest tick of the simulation clock. It is set once before simulation starts and cannot change during a run. The default is 1 ps.

```cpp
// Must be called before sc_start() and before any sc_time objects are created
sc_set_time_resolution(1, SC_NS);   // 1 ns resolution
```

Any `sc_time` value that is not a multiple of the resolution will be **rounded**. This is a common source of subtle bugs when porting models between projects that use different resolutions.

## Internal Representation

Internally, `sc_time` stores time as a 64-bit unsigned integer count of resolution units. This means:

- Maximum simulation time = `2^64 × resolution`
- At 1 ps resolution: maximum ≈ 18,446 seconds (more than enough for chip simulation)
- At 1 fs resolution: maximum ≈ 18.4 seconds (often too small for system-level work)

```cpp
sc_time t(100, SC_NS);
std::cout << t.to_double() << "\n";      // 100 (in current time unit)
std::cout << t.to_seconds() << "\n";    // 1e-7
std::cout << t.value() << "\n";         // raw integer ticks (resolution-dependent)
```

## Arithmetic and Comparison

`sc_time` supports the arithmetic you would expect:

```cpp
sc_time a(10, SC_NS);
sc_time b(3, SC_NS);

sc_time sum  = a + b;     // 13 ns
sc_time diff = a - b;     // 7 ns
sc_time scaled = a * 2;   // 20 ns
bool earlier = b < a;     // true
```

## Setting Time Resolution — Practical Rules

1. Choose resolution **finer than the smallest delay** in your model.
2. Set it **before** creating any `sc_time` objects (including module constructors that use `sc_time`).
3. All modules in a simulation share a single global resolution.

```cpp
int sc_main(int argc, char* argv[]) {
    sc_set_time_resolution(1, SC_PS);  // set early
    MyTop top("top");
    sc_start(1, SC_US);
    return 0;
}
```

## Common Pitfalls

- **Forgetting resolution**: at the default 1 ps, writing `sc_time(0.1, SC_PS)` rounds to 0 — your wait disappears silently.
- **Changing resolution after object creation**: SystemC will throw a run-time error.
- **Large time + fine resolution**: using 1 fs resolution with microsecond delays wastes 64-bit headroom and can slow down the kernel's internal integer math relative to coarser resolutions.

## Worked Example

```cpp
sc_set_time_resolution(1, SC_NS);   // 1 ns grid

sc_time clk_period(10, SC_NS);      // 10 ticks internally
sc_time half = clk_period / 2;      // 5 ns

std::cout << half << "\n";          // prints: 5 ns
```

If you had set resolution to 1 ps, the same code would work but `clk_period` would store `10000` internally.

## Interview Answer

> "`sc_time` stores simulation durations as integer multiples of the global time resolution. The resolution is set once before `sc_start()` and determines the finest granularity of time in the entire simulation. Values finer than the resolution are rounded, so you must choose a resolution smaller than the shortest delay in your model."
