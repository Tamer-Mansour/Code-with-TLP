# Interview Drill: Scheduling Algorithm Questions

Scheduling algorithm questions appear regularly in systems programming interviews at companies building operating systems, databases, cloud infrastructure, and game engines. This lesson gives you the crisp answers that interviewers want, along with the reasoning behind them.

## High-Frequency Interview Questions

---

### 1. "What is the convoy effect, and which algorithm causes it?"

**Crisp answer:** The convoy effect occurs in FCFS when one long CPU-bound process holds the CPU while many short processes queue behind it. I/O devices sit idle because their associated processes cannot complete their brief CPU bursts. It is caused by FCFS's lack of preemption.

**Follow-up pitfall:** Interviewers may ask if Round Robin also causes a convoy effect. It does not — the quantum limit prevents any one process from monopolizing the CPU.

---

### 2. "Which algorithm minimizes average waiting time?"

**Crisp answer:** Shortest-Job-First (SJF) in its non-preemptive form is provably optimal for average waiting time among non-preemptive algorithms. The preemptive version — Shortest-Remaining-Time First (SRTF) — is globally optimal for average waiting time across all algorithms.

**Nuance to add:** SJF requires knowing future burst times, which is impossible in practice. Real systems estimate them using an exponential moving average.

---

### 3. "Can SJF lead to starvation? How do you fix it?"

**Crisp answer:** Yes. If a stream of short jobs keeps arriving, a long job may wait indefinitely. The standard fix is **aging**: incrementally increase a waiting process's effective priority (or equivalently, decrease its effective burst estimate) the longer it waits, so it eventually wins the scheduling race.

---

### 4. "What happens to Round Robin when the time quantum approaches infinity?"

**Crisp answer:** Round Robin degenerates into FCFS. Each process holds the CPU until it finishes (or blocks), because the quantum never expires. Preemption effectively disappears.

**Inverse:** When quantum → 0, RR approximates **processor sharing** — all processes appear to run simultaneously — but context-switch overhead dominates and CPU utilization collapses.

---

### 5. "How do you choose the right time quantum for Round Robin?"

**Crisp answer:** A good rule of thumb is to set the quantum so that roughly 80% of CPU bursts complete within one quantum. This minimizes unnecessary context switches while still keeping response time bounded. The worst-case response time is (n−1) × quantum, so you can derive a maximum quantum from your SLA: quantum ≤ response_SLA / (n − 1).

---

### 6. "Compare the response time of FCFS, SJF, and RR."

**Crisp answer:**
- **FCFS**: Poor response time. A process behind a long job waits the full duration of that job before even starting.
- **SJF**: Good for short processes (they run immediately if the CPU is free), but a long process has terrible response time.
- **Round Robin**: Best bounded response time. Every process gets the CPU within (n−1) × quantum milliseconds.

---

### 7. "What is turnaround time? How is it different from waiting time?"

**Crisp answer:**
- **Turnaround time** = time from process arrival to process completion = CT − arrival.
- **Waiting time** = time spent ready but not running = TAT − burst.

Turnaround includes both waiting and actual execution. Waiting time measures only the scheduling delay.

---

### 8. "Given this set of processes, compute average waiting time for SJF."

Work the formula:
1. Sort eligible processes by burst at each scheduling decision.
2. Compute completion time: `CT = previous CT + burst`.
3. `TAT = CT − arrival`, `WT = TAT − burst`.
4. Average WT = sum(WT) / n.

**Template answer structure for any calculation question:**

```
"At time T, processes A, B, C are eligible.
 I pick the shortest (C, burst=2). It finishes at T+2.
 Now B is eligible (arrived earlier), burst=4, finishes at T+6.
 ... Compute each WT, sum, divide."
```

---

## Rapid-Fire Summary Table

| Question                              | Answer in ≤ 10 words                              |
|---------------------------------------|----------------------------------------------------|
| FCFS worst flaw?                      | Convoy effect — long job blocks all short jobs      |
| SJF optimal for?                      | Minimum average waiting time                       |
| SJF main problem?                     | Burst time unknown; starvation possible             |
| RR advantage over SJF?                | Bounded response time; no starvation               |
| RR disadvantage vs SJF?              | Higher context-switch overhead; worse avg WT        |
| Quantum too small consequence?        | Context-switch overhead dominates; CPU wasted       |
| Quantum too large consequence?        | Degrades to FCFS; poor response time                |
| How modern OSes improve on all three? | Multi-level feedback queues combining all three     |

## One Thing to Always Say

If asked to compare scheduling algorithms in an interview, close with: *"Real-world schedulers like Linux CFS and Windows thread scheduler use multi-level feedback queues that adapt the scheduling strategy dynamically based on each process's observed behavior."* This shows you understand theory and practice.
