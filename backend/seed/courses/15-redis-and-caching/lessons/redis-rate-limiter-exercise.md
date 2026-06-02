# Exercise: Simulate a Fixed-Window Rate Limiter

In this exercise you will implement a fixed-window rate limiter in pure Python — no Redis required. Your program reads a sequence of timestamped API requests and outputs whether each request is **ALLOW** or **DENY** based on a per-user limit within a fixed time window.

This mirrors exactly what `INCR` + `EXPIRE` does in Redis, and builds the mental model you need to implement it for real.

## Problem statement

See the prompt file for full specification.
