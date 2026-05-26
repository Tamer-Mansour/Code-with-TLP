# Quiz: CI/CD and DevOps

**Q1. What is the primary goal of Continuous Integration?**
- [ ] Automatically deploy every commit to production without human approval
- [x] Detect integration problems early by merging frequently and running automated builds and tests on every change
- [ ] Replace manual QA and testing teams entirely
- [ ] Package the application into a Docker container on every commit

**Q2. In a Blue/Green deployment strategy:**
- [ ] Traffic is gradually shifted from old to new over several days
- [x] Two identical environments exist; traffic switches atomically from the old (blue) to the new (green)
- [ ] Only 5% of users see the new version first, then ramp increases gradually
- [ ] The old version is shut down completely before the new one starts

**Q3. What problem do Docker containers primarily solve?**
- [ ] They make application code execute faster
- [ ] They replace the need for automated CI pipelines
- [x] They package an application and all its runtime dependencies so it runs consistently across different environments
- [ ] They provide version control for application source code

**Q4. An SLO (Service Level Objective) is:**
- [ ] A legally binding contract with customers specifying uptime guarantees
- [ ] The specific metric being measured (e.g., request latency at p99)
- [x] An internal target for a service quality metric (e.g., 99.9% of requests succeed within 500 ms)
- [ ] An alert rule that pages on-call engineers when thresholds are exceeded

**Q5. "Infrastructure as Code" (IaC) means:**
- [ ] Writing automation scripts to deploy application code manually via SSH
- [ ] Using a cloud console dashboard to provision and manage resources
- [x] Defining cloud infrastructure in versioned configuration files that are reviewed and applied like application code
- [ ] Monitoring application performance metrics through a code-based dashboard

**Q6. Which observability "pillar" follows a single request as it flows through multiple services, recording timing at each step?**
- [ ] Logs
- [ ] Metrics
- [x] Distributed tracing
- [ ] Alerting
