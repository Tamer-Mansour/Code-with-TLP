# Quiz: CPU Scheduling

**Q1. Which scheduling algorithm guarantees the minimum average waiting time for a batch of processes that all arrive at the same time?**

- [ ] FCFS (First-Come, First-Served)
- [x] SJF (Shortest Job First)
- [ ] Round-Robin with quantum=1ms
- [ ] Priority scheduling with aging

**Q2. What is the "convoy effect" in FCFS scheduling?**

- [ ] Short processes are always scheduled before long ones regardless of arrival time
- [x] Short processes get stuck waiting behind a long-running process, causing high average waiting time
- [ ] Long processes are periodically preempted to allow short ones to run
- [ ] The CPU idles waiting for all processes to arrive before starting any

**Q3. In Round-Robin scheduling, what happens when a process's time quantum expires before it finishes?**

- [ ] The process is terminated and must be restarted from scratch
- [ ] The process is moved to the waiting (blocked) queue until its next I/O event
- [x] The process is preempted and placed at the back of the ready queue
- [ ] The scheduler doubles the quantum for that process on its next turn

**Q4. Turnaround time is defined as:**

- [ ] Time the process spends waiting in the ready queue only
- [ ] Time from the first CPU use to process completion
- [x] Total elapsed time from process submission to completion (finish time minus arrival time)
- [ ] Time from submission to first CPU use (also called response time)

**Q5. Priority scheduling can suffer from starvation. The standard mitigation is:**

- [ ] Reducing all process priorities to zero after one quantum expires
- [ ] Switching to Round-Robin for all low-priority processes only
- [x] Aging: gradually increasing a waiting process's effective priority the longer it waits
- [ ] Preempting high-priority processes at a random interval to give others a chance

**Q6. Linux's Completely Fair Scheduler (CFS) models fairness by tracking:**

- [ ] How many system calls each process has made since its last context switch
- [ ] The number of page faults per process per second
- [x] The virtual runtime of each process — how much CPU time it has consumed, weighted by its priority (nice value)
- [ ] Each process's resident memory footprint relative to the system total
