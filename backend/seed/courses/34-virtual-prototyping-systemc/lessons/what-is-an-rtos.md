# What Is an RTOS and What Makes It Real-Time?

A Real-Time Operating System (RTOS) is an operating system designed to execute tasks within guaranteed time bounds. The key word is *guaranteed* — not "usually fast", not "fast on average". Real-time means **deterministic**: given a specific event, the system must respond within a specific deadline, every single time.

## What "Real-Time" Actually Means

Real-time is not a synonym for fast. A system that averages 1 µs response but occasionally spikes to 10 ms is NOT real-time. A system that always responds in exactly 5 ms — even under worst-case load — IS real-time.

| Class | Definition | Example |
|---|---|---|
| Hard real-time | Missing a deadline is a system failure | Airbag ECU, pacemaker, flight control |
| Soft real-time | Missing occasional deadlines degrades quality | Video streaming, audio playback |
| Firm real-time | Missing a deadline makes the result useless, but is not catastrophic | Industrial sensor sampling |

## The RTOS Scheduler

The heart of an RTOS is its **preemptive priority scheduler**. Tasks are assigned a fixed priority. The scheduler always runs the highest-priority *ready* task. If a higher-priority task becomes ready (e.g., due to an interrupt or a semaphore being given), the scheduler immediately preempts the current task and switches to it.

```
Priority   Task       State
   5       Motor ISR  Ready  ← runs first
   4       Control    Blocked (waiting for queue)
   3       Sensor     Running → preempted
   2       Comms      Ready
   1       Idle       Ready
```

The scheduler runs at each **tick** (e.g., every 1 ms on a 1 kHz tick) and after every RTOS API call that could unblock a higher-priority task.

## Core RTOS Concepts

**Task (Thread):** An independent function with its own stack, priority, and state (Running / Ready / Blocked / Suspended).

**Context Switch:** Saving the CPU registers of the preempted task and loading those of the next task. On Cortex-M, this includes R0–R12, LR, PC, xPSR, and floating-point registers if FPU is used. A typical context switch takes < 1 µs.

**Tick Interrupt:** A periodic hardware timer interrupt that drives the scheduler. Tick period is a key tuning parameter: shorter = finer delay resolution but more overhead.

**Semaphore / Mutex:** Synchronisation primitives. A binary semaphore signals between tasks. A mutex adds ownership and priority inheritance to prevent priority inversion.

**Message Queue:** A FIFO buffer that safely passes data from one task (or ISR) to another without explicit locking.

## Worked Example: FreeRTOS Task Creation

```c
#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"

QueueHandle_t g_queue;

// High-priority task: reads sensor, posts to queue
void vSensorTask(void *pvParameters) {
    TickType_t xLastWake = xTaskGetTickCount();
    for (;;) {
        uint16_t sample = adc_read_blocking();
        xQueueSend(g_queue, &sample, 0);
        vTaskDelayUntil(&xLastWake, pdMS_TO_TICKS(10)); // 100 Hz
    }
}

// Lower-priority task: processes data
void vProcessTask(void *pvParameters) {
    uint16_t sample;
    for (;;) {
        if (xQueueReceive(g_queue, &sample, portMAX_DELAY) == pdTRUE) {
            process(sample);
        }
    }
}

int main(void) {
    g_queue = xQueueCreate(8, sizeof(uint16_t));
    xTaskCreate(vSensorTask,  "Sensor",  256, NULL, 5, NULL);
    xTaskCreate(vProcessTask, "Process", 512, NULL, 3, NULL);
    vTaskStartScheduler(); // never returns
}
```

`vTaskDelayUntil` makes `vSensorTask` periodic: it wakes at an *absolute* tick count, not a relative delay from when it finished — preventing drift.

## Popular RTOS Options

| RTOS | Licence | Typical Use |
|---|---|---|
| FreeRTOS | MIT | Widest ecosystem; AWS IoT |
| Zephyr | Apache 2.0 | Linux Foundation; Bluetooth/802.15.4 |
| ThreadX (Azure RTOS) | MIT (Microsoft) | Certified for IEC 61508, DO-178 |
| RTEMS | BSD | Aerospace, space |
| Mbed OS | Apache 2.0 | ARM IoT devices |
| embOS | Commercial | Segger; automotive |

## Common Pitfalls

- **Wrong tick resolution.** A 100 Hz tick (10 ms resolution) cannot schedule a 1 ms periodic task accurately. Increase tick rate or use a hardware timer directly.
- **Forgetting ISR-safe API variants.** Calling `xSemaphoreGive` (not `xSemaphoreGiveFromISR`) from an ISR causes a hard fault or data corruption.
- **Stack undersizing.** Each task needs its own stack. Failing to account for interrupt frame save, function call depth, and printf-style formatting (which is stack-hungry) causes overflow.
- **Treating mutexes as semaphores.** Mutexes carry ownership and priority inheritance; binary semaphores do not. Using a semaphore for mutual exclusion invites priority inversion.

> **Interview answer:** An RTOS is an operating system with a deterministic preemptive scheduler that guarantees task responses within defined deadlines; "real-time" means worst-case latency is bounded, not just that the system is fast on average.
