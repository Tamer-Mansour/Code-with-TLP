# Exercise: Deployment Rolling Update Simulator

A Kubernetes Deployment performs a **rolling update** when you change the pod template (e.g., a new image). The rollout proceeds in waves controlled by two parameters:

- `maxSurge` — how many *extra* pods above the desired count can exist during the rollout.
- `maxUnavailable` — how many pods can be simultaneously unavailable (not running) below the desired count.

At each step, the controller:
1. Scales **up** new pods until `old + new == desired + maxSurge`.
2. Terminates **old** pods until `unavailable <= maxUnavailable` (where `unavailable = desired - new`).
3. Repeats until all pods run the new version.

In this exercise you will simulate this process step-by-step.

> **Further reading:** [Kubernetes Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#rolling-update-deployment) and [The Kubernetes Handbook](https://www.freecodecamp.org/news/the-kubernetes-handbook/) cover rolling update semantics in depth.

See the exercise prompt for the full input/output specification.
