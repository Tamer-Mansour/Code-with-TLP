# Quiz: Processes and Scheduling

**Q1. What does process state `D` (uninterruptible sleep) mean?**
- [ ] The process has been deliberately paused with SIGSTOP
- [ ] The process is a zombie waiting to be reaped
- [x] The process is waiting on kernel I/O and cannot be interrupted, even by SIGKILL
- [ ] The process is idle and consuming no CPU

**Q2. Which two signals can NEVER be caught, blocked, or ignored by user-space code?**
- [ ] SIGTERM and SIGHUP
- [ ] SIGINT and SIGUSR1
- [x] SIGKILL and SIGSTOP
- [ ] SIGKILL and SIGTERM

**Q3. A zombie process (state `Z`) is best described as:**
- [ ] A process consuming excessive CPU that must be killed with SIGKILL
- [ ] A process that has lost its parent and been reparented to init
- [x] A process that has exited but whose parent has not yet called wait() to collect its exit status
- [ ] A process suspended in the background with Ctrl-Z

**Q4. You want a background job to keep running after you close your SSH session. Which command achieves this?**
- [ ] `bg myjob`
- [ ] `jobs -l myjob`
- [x] `nohup ./myjob &`
- [ ] `Ctrl-Z then fg`

**Q5. What does `nice -n 10 ./cpu-heavy.sh` do?**
- [ ] Raises the process priority so it gets more CPU
- [x] Lowers the process priority (higher nice value = lower priority)
- [ ] Limits the process to 10% CPU usage
- [ ] Runs the script at exactly 10 seconds intervals

**Q6. Which crontab field order is correct?**
- [ ] hour minute month day-of-month day-of-week
- [x] minute hour day-of-month month day-of-week
- [ ] day-of-week month day-of-month hour minute
- [ ] minute hour month day-of-month day-of-week

**Q7. You run `kill 1234` with no signal flag. Which signal is sent?**
- [ ] SIGKILL (9)
- [ ] SIGHUP (1)
- [x] SIGTERM (15)
- [ ] SIGINT (2)

**Q8. What is the key advantage of systemd timers over cron for production workloads?**
- [ ] Timers support */5 step syntax; cron does not
- [ ] Timers run jobs as root by default; cron does not
- [x] Timers integrate with journald for automatic logging and support Persistent=true for missed-run recovery
- [ ] Timers are faster because they bypass the kernel scheduler
