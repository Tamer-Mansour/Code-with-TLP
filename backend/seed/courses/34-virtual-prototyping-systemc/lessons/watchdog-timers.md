# Watchdog Timers and System Recovery

A watchdog timer (WDT) is a hardware safety net: a countdown timer that resets the system if the software fails to periodically reset it. If the firmware hangs, deadlocks, or enters an infinite loop, the watchdog fires — returning the system to a known good state without human intervention.

## The Core Concept

The watchdog counter decrements continuously. Firmware must write a specific value ("kick", "pet", or "feed" the watchdog) before the counter reaches zero. If it does reach zero, the watchdog asserts a **system reset** (or sometimes a non-maskable interrupt first).

```
Counter value:  FFFF ... 0100 0099 ... 0001 0000 → RESET!
                          ^--- software must write before here
```

This makes the watchdog a **liveness proof**: it proves the main software loop is still executing.

## Windowed Watchdog (WWDT)

A standard watchdog only checks that you kick it before it expires. A **windowed watchdog** also checks that you do not kick it too early — there is both a minimum and maximum valid window:

```
|-- TOO EARLY (reset) --|-- VALID KICK WINDOW --|-- TOO LATE (reset) --|
0                       W                       T
```

This catches firmware that is stuck in a tight loop kicking the watchdog but never reaching the rest of the application.

## Key Registers

| Register | Purpose |
|---|---|
| `WDTLOAD` / `PR` | Reload value — sets the timeout period |
| `WDTCR` / `CTRL` | Enable, reset/interrupt mode, clock source |
| `WDTSR` / `ICR` | Status / interrupt-clear register |
| `WDTKEY` | Unlock sequence — prevents accidental writes (e.g., write `0xCAFE` then `0xBEEF`) |

Many watchdogs require a **magic unlock sequence** before any control register can be written, preventing a runaway program from disabling the watchdog.

## Timeout Calculation

```
Timeout = WDTLOAD × T_clk
```

For a 32 kHz watchdog clock and a 2-second timeout:

```
WDTLOAD = 2 s × 32000 Hz = 64000 = 0xFA00
```

## Firmware Pattern

```c
void watchdog_init(void) {
    WDT->KEY  = 0xCAFE;         // unlock
    WDT->KEY  = 0xBEEF;
    WDT->LOAD = 0xFA00;         // 2-second timeout
    WDT->CTRL = WDT_CTRL_EN |   // enable
                WDT_CTRL_RESEN; // reset on expire
}

void watchdog_kick(void) {
    WDT->KEY  = 0xCAFE;
    WDT->KEY  = 0xBEEF;
    WDT->LOAD = 0xFA00;         // reload the counter
}

void main_loop(void) {
    watchdog_init();
    while (1) {
        do_work();
        watchdog_kick();  // must reach here within 2 s
    }
}
```

## SystemC Model Sketch

```cpp
SC_MODULE(Watchdog) {
    sc_out<bool> reset_out;
    sc_in<bool>  clk;

    uint32_t load_val   = 0;
    uint32_t counter    = 0;
    bool     enabled    = false;

    void tick() {
        if (!enabled) return;
        if (counter == 0) {
            reset_out.write(true);    // assert system reset
            wait(10, SC_NS);
            reset_out.write(false);
            counter = load_val;       // self-reload after reset
        } else {
            --counter;
        }
    }

    void kick(uint32_t new_load) {
        counter = new_load;
        load_val = new_load;
    }

    SC_CTOR(Watchdog) {
        SC_METHOD(tick);
        sensitive << clk.pos();
    }
};
```

## Early Warning Interrupt

Some watchdogs fire an NMI (non-maskable interrupt) a few cycles before the final reset. This gives firmware a last chance to:

- Log diagnostic information to non-volatile memory.
- Capture a stack trace or fault code.
- Perform a clean shutdown of external hardware.

## Common Pitfalls

- **Kicking inside an ISR** — the ISR may execute fine while the main thread is deadlocked; the watchdog is fooled. Kick only in the main loop.
- **Disabling the watchdog in production** — developers often disable it during debug and forget to re-enable it. Use a build flag to enforce it in release.
- **Wrong clock source** — if the watchdog runs from the main PLL and the PLL fails, the watchdog itself stops. Use an independent low-speed oscillator (e.g., 32 kHz RTC crystal) for safety-critical watchdogs.
- **Forgetting the unlock sequence** — on protected watchdogs, writes without the correct key are silently ignored.

> **Interview answer:** A watchdog timer resets the system if firmware fails to "kick" it within a deadline. It proves liveness of the main loop. A windowed watchdog adds a minimum kick window to also detect tight-loop lockups. The key design rule is to kick only from the main task, never from an interrupt handler.
