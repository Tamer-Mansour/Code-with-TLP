# Exercise: Container Resource Limit Checker

Practice applying cgroup concepts by simulating Docker's CPU share and memory limit enforcement.

## Background

Docker uses Linux **cgroups** to enforce resource limits on containers:

- **Memory**: hard ceiling in MB — requests above the limit are denied.
- **CPU shares**: a relative weight. A container's effective CPU percentage is `(its_shares / total_all_shares) * 100`, rounded **down**.

Given a set of containers and their resource limits, determine whether incoming resource requests should be allowed or denied.

## What You'll Practice

- Understanding CPU share arithmetic
- Applying memory constraints
- Reading multi-section stdin input
