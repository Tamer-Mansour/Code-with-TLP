# Containers vs Virtual Machines

Containers and VMs both provide **isolation** for workloads, but they operate at fundamentally different layers of the stack. Knowing precisely where they differ — and when to choose each — is a common system design interview question.

## The Core Difference

| Dimension | Virtual Machine | Container |
|---|---|---|
| What is isolated | Entire OS + kernel | Processes only; shared kernel |
| Isolation boundary | Hardware (VMM) | OS (namespaces + cgroups) |
| Guest kernel | Each VM has its own | All containers share the host kernel |
| Startup time | 10 s – several minutes | < 1 second (often milliseconds) |
| Image size | GBs (full OS) | MBs (app + libs only) |
| Memory overhead | 100s MB per VM (full OS) | A few MB per container |
| Security isolation | Strong (hardware boundary) | Weaker (kernel attack surface shared) |
| Use case | Multi-tenant, different OSes | Microservices, CI/CD, packaging |

## Virtual Machines — The Full Stack

```
┌────────────────────────────────────────┐
│  App  │  App  │  App  │  App           │
├───────┴───────┴───────┘                │
│  Guest OS (full kernel per VM)         │
├────────────────────────────────────────┤
│  Hypervisor (VT-x / AMD-V)             │
├────────────────────────────────────────┤
│  Physical Hardware                     │
└────────────────────────────────────────┘
```

The VMM presents virtual hardware; each guest boots a complete OS. A security exploit in one VM's kernel cannot directly affect another VM because the VMM enforces a hardware boundary.

## Containers — Process Isolation on a Shared Kernel

```
┌──────────┬──────────┬──────────┐
│  App A   │  App B   │  App C   │  (each in own container)
├──────────┴──────────┴──────────┤
│     Host Linux Kernel          │  ← all containers share this
├────────────────────────────────┤
│     Physical Hardware          │
└────────────────────────────────┘
```

Containers use Linux **namespaces** to give each group of processes its own view of PIDs, network, filesystem, users, etc., and **cgroups** to enforce CPU/memory/I/O resource limits. From inside the container, it looks like a private machine. But they all make system calls to the same kernel.

## Worked Example: Startup Time

```bash
# Starting a VM (KVM + cloud-init)
$ time virsh start my-vm
# real: 0m18.4s   (BIOS POST, kernel boot, systemd)

# Starting a container (Docker)
$ time docker run --rm alpine echo "hello"
# real: 0m0.3s    (fork + exec; no kernel boot)
```

This difference is why containers dominate CI/CD pipelines — spinning up 500 container-based test runners in seconds is practical; doing the same with VMs is not.

## Security Isolation Trade-Off

**VMs:** A malicious guest needs to exploit the hypervisor (a small, well-audited codebase) to escape. Hypervisor CVEs exist but are rare.

**Containers:** A malicious container needs to exploit the **Linux kernel** (millions of lines of code) to escape to other containers or the host. The kernel attack surface is vastly larger. Container escapes happen more frequently (e.g., runc CVE-2019-5736, Dirty Pipe CVE-2022-0847).

Mitigations for containers:
- Run as non-root (`USER` in Dockerfile).
- Use seccomp profiles to restrict syscalls.
- Use AppArmor/SELinux mandatory access control.
- Use **gVisor** (Google) or **Kata Containers** — hybrid: container interface, VM-level isolation.

## When to Use Each

**Use VMs when:**
- Running different OS kernels (Windows + Linux on same host).
- Strong multi-tenant isolation is required (public cloud, financial services).
- Compliance mandates hardware-level isolation.

**Use containers when:**
- Packaging and shipping application dependencies.
- High-density microservices (hundreds per host).
- Fast CI/CD pipelines requiring rapid scale-up/down.
- All workloads trust the same kernel.

## The Modern Answer: Both

Production systems routinely layer them: **containers inside VMs**. AWS Fargate runs ECS/EKS containers inside Firecracker microVMs (a lightweight VMM). This gives:

- VM-level security isolation between customers.
- Container-level packaging and startup speed.
- Firecracker boots in ~125 ms, far faster than a full VM.

> **Interview answer:** "VMs virtualize full hardware so each guest has its own kernel — strong isolation, higher overhead. Containers share the host kernel and use namespaces + cgroups for isolation — lightweight and fast but smaller security boundary. Production systems often combine them: containers inside lightweight VMs (Firecracker, Kata)."
