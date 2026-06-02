# Interview Drill: Scheduling Fundamentals

This lesson distills the most frequently asked CPU scheduling questions in software engineering and systems programming interviews. Each question is followed by the ideal answer structure — concise, accurate, and signaling deep understanding.

---

## Q1: What is the difference between the scheduler and the dispatcher?

**The pitfall:** Candidates merge both into a vague "the OS picks the next process."

**Strong answer:**
> "The scheduler is the policy component — it selects which process runs next from the ready queue. The dispatcher is the mechanism — it performs the actual context switch: saving the outgoing process's registers into its PCB, loading the incoming process's state, switching address spaces if needed, and returning to user mode. Dispatch latency is the measurable cost of this operation."

---

## Q2: What is dispatch latency and why does it matter?

**Strong answer:**
> "Dispatch latency is the time between the scheduler selecting a process and that process executing its first instruction. It includes register save/restore, potential TLB flush when switching address spaces, and the privileged return to user mode. It matters because it is pure overhead — no useful work is done during it. Choosing a very small time quantum in round-robin scheduling can make dispatch latency a significant fraction of total CPU time."

---

## Q3: What is the difference between preemptive and non-preemptive scheduling?

**Strong answer:**
> "In non-preemptive scheduling, a process keeps the CPU until it voluntarily yields (terminates or blocks on I/O). In preemptive scheduling, the OS can forcibly evict a running process — via a timer interrupt or because a higher-priority process became ready. All modern general-purpose OSes (Linux, Windows NT+, macOS) use preemptive scheduling because it ensures responsiveness and prevents a single CPU-bound process from starving others."

---

## Q4: Under what four conditions does the scheduler make a decision?

**Strong answer:**
> "1) A process transitions from RUNNING to BLOCKED (I/O wait). 2) A process terminates. 3) A timer interrupt expires the running process's time quantum (preemptive only). 4) A process moves from BLOCKED to READY after I/O completion and may preempt the current process (preemptive only). Conditions 1 and 2 apply to both preemptive and non-preemptive schedulers; 3 and 4 apply only to preemptive ones."

---

## Q5: Define turnaround time, waiting time, and response time. How are they related?

**Strong answer:**
> "Turnaround time = completion time - arrival time — total elapsed time for a process.
> Waiting time = turnaround time - CPU burst time — time spent idle in the ready queue.
> Response time = first CPU start time - arrival time — time until the process first gets CPU.
> For non-preemptive algorithms, response time equals waiting time. For preemptive algorithms (Round Robin), response time is lower because the process gets CPU quickly even if it doesn't finish."

---

## Q6: What is the convoy effect and which algorithm causes it?

**Strong answer:**
> "The convoy effect occurs in FCFS when one long CPU-bound process arrives before many short I/O-bound processes. The short processes must wait for the long one to finish, leading to high average waiting time and low CPU + I/O utilization. SJF eliminates the convoy effect by always running the shortest available burst first."

---

## Q7: How does a scheduler estimate burst length for SJF?

**Strong answer:**
> "Most implementations use **exponential averaging**: τ_{n+1} = α·t_n + (1-α)·τ_n, where t_n is the measured burst length and τ_n is the previous estimate. With α = 0.5, recent history is weighted equally with older history. This makes SJF practical without requiring advance knowledge of burst lengths."

---

## Q8: What is a CPU-bound vs I/O-bound process, and how should the scheduler treat them?

**Strong answer:**
> "A CPU-bound process has long CPU bursts and rarely blocks — examples: video encoder, scientific simulation. An I/O-bound process has short CPU bursts and frequently blocks — examples: web server, text editor. Schedulers typically give I/O-bound processes higher priority because they voluntarily release the CPU quickly, allowing the disk and network to stay busy in parallel. Prioritizing them improves overall system throughput and user responsiveness."

---

## Quick-Reference Formulas

```
Turnaround  = Completion - Arrival
Waiting     = Turnaround - Burst
Response    = FirstCPUStart - Arrival
Throughput  = Processes_completed / Total_time
```

## One-Line Summaries for Rapid Recall

| Topic | One-liner |
|-------|-----------|
| Scheduler | Chooses who runs next (policy) |
| Dispatcher | Performs context switch (mechanism) |
| Dispatch latency | Cost of the switch — pure overhead |
| Non-preemptive | Process runs until it yields voluntarily |
| Preemptive | OS can evict a running process via timer |
| FCFS weakness | Convoy effect from long jobs blocking short ones |
| SJF advantage | Minimizes average waiting time |
| Response time | How soon a process first touches the CPU |
