# Hardware Timers and Counters

Hardware timers are among the most versatile peripherals on any microcontroller. They underpin delays, PWM, input capture, event counting, and RTOS tick generation — all without consuming CPU cycles once configured. Understanding their internals is essential for both embedded development and virtual platform modeling.

## Core Architecture

A hardware timer is built around three elements:

1. **Prescaler (PSC)** — divides the input clock before the counter sees it.
2. **Counter (CNT)** — increments (or decrements) on each tick of the divided clock.
3. **Auto-Reload Register (ARR)** — defines the period; the counter resets to zero (or to ARR for down-counting) when it reaches ARR.

```
f_input → [÷(PSC+1)] → [CNT: 0 ... ARR] → overflow event / interrupt
```

The effective timer frequency:

```
f_timer = f_input / (PSC + 1)
```

Period of one timer cycle:

```
T_period = (ARR + 1) / f_timer = (ARR + 1) × (PSC + 1) / f_input
```

## Generating a Precise Delay

To generate a 10 ms interrupt on a 72 MHz timer:

```
Target: T = 10 ms = 0.01 s
Choose PSC = 71  →  f_timer = 72 MHz / 72 = 1 MHz  (1 µs per tick)
ARR = T × f_timer − 1 = 10000 − 1 = 9999
```

```c
TIM2->PSC = 71;         // 1 MHz timer clock
TIM2->ARR = 9999;       // overflow every 10 ms
TIM2->DIER |= TIM_DIER_UIE;  // update interrupt enable
TIM2->CR1  |= TIM_CR1_CEN;   // start
```

## Counter Modes

| Mode | CNT behavior | Use case |
|---|---|---|
| Up-counting | 0 → ARR, then overflow | Delays, PWM, RTOS tick |
| Down-counting | ARR → 0, then underflow | Some PWM applications |
| Center-aligned | 0 → ARR → 0, repeat | Center-aligned PWM (motor drives) |
| One-pulse | Counts once then stops | Single-shot pulse |

## Capture/Compare Channels

Advanced timers have capture/compare channels (CCR registers) that share the counter:

- **Output Compare (OC)**: when CNT == CCRn, trigger an action (toggle a pin, set/clear it). This is how PWM works.
- **Input Capture (IC)**: when a pin edge is detected, the current CNT value is latched into CCRn. Used to measure pulse widths and frequencies.

### Measuring Frequency with Input Capture

```c
// On rising edge: save timestamp in CCR1
// On next rising edge: save in CCR2
// Period = (CCR2 - CCR1) / f_timer
// Frequency = f_timer / (CCR2 - CCR1)
```

## Event Counting Mode

Timers can be clocked from an **external pin** instead of the internal clock. Each rising (or falling) edge on the input increments CNT. This turns the timer into a hardware event counter — counting encoder pulses, button presses, or network packets without CPU intervention.

## SystemC Model Sketch

```cpp
SC_MODULE(HWTimer) {
    sc_in<bool>  clk;
    sc_out<bool> overflow_irq;

    uint32_t psc_reg = 0;
    uint32_t arr_reg = 0xFFFF;
    uint32_t cnt     = 0;
    uint32_t psc_cnt = 0;    // prescaler divider state
    bool     enabled = false;

    void tick() {
        if (!enabled) return;

        ++psc_cnt;
        if (psc_cnt <= psc_reg) return;  // not yet a timer tick
        psc_cnt = 0;

        ++cnt;
        if (cnt > arr_reg) {
            cnt = 0;
            overflow_irq.write(true);    // pulse the interrupt line
            wait(SC_ZERO_TIME);
            overflow_irq.write(false);
        }
    }

    SC_CTOR(HWTimer) {
        SC_METHOD(tick);
        sensitive << clk.pos();
    }
};
```

## RTOS Tick Timer

Most RTOSes (FreeRTOS, Zephyr, ThreadX) configure one hardware timer to generate the **system tick** — a periodic interrupt (typically every 1 ms) that drives context switches. The RTOS tick ISR:

1. Increments the tick counter.
2. Unblocks any tasks whose delay has expired.
3. Triggers a context switch if a higher-priority task is ready.

The RTOS requires the tick timer never to drift — using a hardware timer with a fixed reload value (not a software delay) is mandatory.

## Common Pitfalls

- **Off-by-one in ARR** — the period is `(ARR + 1)` ticks, not `ARR`. A common mistake sets `ARR = 10000` expecting 10 ms but gets 10.001 ms.
- **Prescaler + ARR overflow** — both are 16-bit on many timers; long periods require careful calculation or chaining two timers.
- **Not waiting for timer to sync** — writing PSC/ARR while the counter is running takes effect at the next update event; reading CNT immediately after write gives the old value.
- **Forgetting to clear the update flag** — if the update interrupt flag (UIF) is not cleared in the ISR, the ISR fires again immediately.

> **Interview answer:** A hardware timer counts clock ticks after prescaling, generating an interrupt when the counter reaches the auto-reload value. Period = (ARR+1)(PSC+1)/f_clk. Capture/compare channels extend timers for PWM generation and pulse-width measurement. The off-by-one error in ARR is the most common timer configuration mistake.
