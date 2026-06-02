# Bare-Metal vs RTOS: When Do You Need an OS?

One of the first architectural decisions in any embedded project is whether to use an RTOS or go bare-metal. Getting this wrong early is expensive — refactoring a grown bare-metal codebase into RTOS tasks, or stripping out an RTOS to recover latency, both take weeks.

## What Is Bare-Metal?

Bare-metal means your firmware runs directly on the hardware with no operating system layer. Your code is the only software on the processor. You handle everything: the super-loop, interrupts, timing, and state machines.

```c
int main(void) {
    hal_init();

    while (1) {               // the "super-loop"
        sensor_poll();        // blocking or polling
        compute_control();
        update_outputs();
        low_power_sleep();
    }
}

void TIM2_IRQHandler(void) {  // hardware interrupt — runs any time
    timestamp_tick++;
    TIM2->SR &= ~TIM_SR_UIF;
}
```

**Strengths:**
- Minimal RAM footprint (no OS kernel overhead — often < 1 KB).
- Fully deterministic: you know exactly what runs when.
- No context-switch jitter.
- Simple to reason about for small systems.

**Weaknesses:**
- State machines grow complex as features are added.
- Hard to add concurrency cleanly (everything must be non-blocking or carefully ISR-driven).
- No built-in services: no semaphores, no message queues, no timers abstraction.

## What Does an RTOS Add?

An RTOS gives you **preemptive multitasking**: multiple logical threads of execution, each with its own stack, that the scheduler switches between based on priority and readiness.

Core RTOS primitives:

| Primitive | Purpose |
|---|---|
| Task / Thread | Independent execution context with its own stack |
| Semaphore | Signal between tasks (binary or counting) |
| Mutex | Mutual exclusion with priority inheritance |
| Message Queue | Pass data safely between tasks or ISRs |
| Timer | Software timer callbacks |
| Event Group | Multiple flags combined with AND/OR logic |

```c
// FreeRTOS example: two tasks running "concurrently"
void sensor_task(void *pvParams) {
    for (;;) {
        int val = adc_read();
        xQueueSend(data_queue, &val, portMAX_DELAY);
        vTaskDelay(pdMS_TO_TICKS(10));   // yield for 10 ms
    }
}

void control_task(void *pvParams) {
    int val;
    for (;;) {
        xQueueReceive(data_queue, &val, portMAX_DELAY);
        set_pwm(pid_compute(val));
    }
}
```

## The Decision Framework

Ask these questions in order:

1. **Do you have fewer than ~3 concurrent activities that can all be driven by ISRs or a single loop?**
   - Yes → bare-metal is almost certainly simpler and leaner.

2. **Do any activities need to block (wait for I/O, delay) independently of each other?**
   - Yes → an RTOS makes the concurrency manageable.

3. **Is your RAM budget under ~4 KB total?**
   - Yes → the RTOS kernel overhead (typically 5–20 KB flash, 2–8 KB RAM) may be prohibitive.

4. **Do you need inter-task communication, shared resource protection, or software timers?**
   - Yes → RTOS primitives prevent you from re-inventing these (often incorrectly).

5. **Are there hard real-time deadlines that differ by task?**
   - Yes → RTOS priority assignment lets high-priority tasks preempt low-priority ones reliably.

## Common Pitfalls

- **Priority inversion.** Task A (high) waits on a mutex held by Task C (low), which is preempted by Task B (medium) — A is starved. Solution: use a mutex with priority inheritance (most RTOS implementations support this).
- **Stack overflow.** Each RTOS task has its own stack. Undersizing any task's stack causes silent corruption. Enable RTOS stack-overflow detection hooks in development.
- **Adding an RTOS to "fix" a design problem.** An RTOS is not a silver bullet. If your architecture is wrong, an RTOS adds overhead and complexity without solving the root cause.
- **Calling blocking OS APIs from an ISR.** Most RTOS APIs must not be called from interrupt context; use the `FromISR` variants (e.g., `xQueueSendFromISR` in FreeRTOS).

## Rule of Thumb

| Project profile | Recommendation |
|---|---|
| 1–3 tasks, simple state machine, < 8 KB RAM | Bare-metal |
| 4+ concurrent activities, I/O blocking, shared data | RTOS |
| Rich OS needed (networking stack, filesystem, UI) | Embedded Linux |

> **Interview answer:** Go bare-metal when concurrency is simple and every byte of RAM counts; choose an RTOS when you have multiple independent activities that need to block or share data safely, where RTOS primitives (tasks, queues, semaphores) manage the complexity that a super-loop cannot.
