# Exercise: Module Hierarchy Port Binding Validator

## Problem Statement

In SystemC, each port must be bound exactly once during elaboration. Unbound ports and double-bound ports are both fatal errors caught before simulation starts.

You are given a module hierarchy description. Each module has a name, a list of ports, and a list of bindings. A binding connects a port of one module instance to a signal or parent port.

**Validation rules:**
1. Every declared port must appear in exactly one binding.
2. A port cannot be bound more than once.
3. A binding may not reference an undeclared port.

For each module, print `MODULE <name>: OK` if all bindings are valid, or list each error as:
- `UNDECLARED_PORT: <port_name>` for bindings referencing nonexistent ports
- `DOUBLE_BOUND: <port_name>` for ports bound more than once
- `UNBOUND_PORT: <port_name>` for unbound ports

Print errors in order: UNDECLARED first (in binding order), then DOUBLE_BOUND (in binding order of the second occurrence), then UNBOUND_PORT (in declaration order).

## Input Format

- Line 1: `M` (number of modules, 1 <= M <= 5)
- For each module:
  - Line: `<module_name> <P> <B>` (P ports, B bindings)
  - P lines: port names
  - B lines: port names being bound (may repeat or include unknown names)

## Output Format

- For each module: either `MODULE <name>: OK` or `MODULE <name>:` followed by error lines

## Constraints

- 1 <= M <= 5
- 1 <= P <= 10
- 0 <= B <= 15
- Port names contain only letters, digits, and underscores

## Sample Input

```
2
cpu_core 3 3
clk_port
reset_port
data_port
clk_port
data_port
data_port
bus_bridge 2 1
req_port
ack_port
req_port
```

## Sample Output

```
MODULE cpu_core:
DOUBLE_BOUND: data_port
UNBOUND_PORT: reset_port
MODULE bus_bridge:
UNBOUND_PORT: ack_port
```

## Additional Example

Input:
```
1
timer 2 2
clk_in
irq_out
clk_in
irq_out
```

Output:
```
MODULE timer: OK
```
