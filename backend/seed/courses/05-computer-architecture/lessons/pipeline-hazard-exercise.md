# Exercise: Pipeline Hazard Detector

This exercise puts your pipelining knowledge to the test. You will simulate a 5-stage in-order pipeline and count the total number of stall cycles required to resolve RAW (Read After Write) data hazards when no forwarding is available.

## Background

In a 5-stage pipeline (IF → ID → EX → MEM → WB):

- Source registers are **read in the ID stage**.
- Results are **written in the WB stage**.
- Without forwarding, a consumer must wait until the producer's WB stage has completed before its own ID stage can safely read the updated value.

When this constraint is violated, the hazard detection unit inserts **stall cycles** (also called pipeline bubbles), pausing the front end of the pipeline until the value is ready.

## Key Insight

If instruction I finishes its WB stage at cycle W, and instruction J reads a register written by I at cycle D (ID stage), then:

- If `W > D`: stall cycles needed = `W - D`
- If `W <= D`: no stall needed

Stalls inserted for earlier hazards shift all subsequent instruction timings, which can eliminate or reduce later hazards.

## Challenge

Implement the simulation for sequences of up to 20 instructions and compute the total stall count.
