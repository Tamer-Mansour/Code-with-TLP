# Simulate an Event Queue and Report Fire Order

In this exercise you will implement a simplified SystemC-style event queue simulator in Python. The scheduler manages a set of named events, each scheduled at a specific simulation time. Your job is to process the queue and report the order in which events fire.

## What You Will Implement

You will build a priority-queue–based event scheduler that:

1. Accepts a list of events, each with a name and a scheduled fire time (in nanoseconds).
2. Processes the queue in ascending time order.
3. When multiple events share the same fire time, outputs them in **alphabetical order** (mimicking a deterministic tie-break policy).
4. Prints each event in the format `T=<time>ns <name>`.

## Why This Matters

The SystemC kernel's global event queue is at the core of event-driven simulation. When you call `my_event.notify(10, SC_NS)`, an entry is inserted into this queue. The kernel repeatedly pops the earliest entry, advances simulation time, and fires the event. Implementing this queue by hand gives you an exact mental model of what the C++ kernel does under the hood.

## Skills Practiced

- Priority queue / min-heap data structures
- Deterministic tie-breaking (alphabetical) for same-timestamp events
- Parsing simple structured input
- Simulating event-driven scheduling logic

## Getting Started

Your solution should read from standard input and print to standard output. The prompt file describes the exact input/output format, constraints, and sample cases.

Study the sample carefully: note that ties at the same timestamp are broken alphabetically by event name — this is the key ordering rule.
