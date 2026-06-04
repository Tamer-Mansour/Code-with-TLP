# Video: Virtualization, Containers, and Hypervisors

This video unit covers the core concepts of system virtualization — how multiple operating systems can run on a single physical machine — and the lighter-weight alternative of Linux containers.

## What You Will Learn

- Type 1 (bare-metal) vs. Type 2 (hosted) hypervisors and their performance trade-offs
- The x86 virtualization challenge and how Intel VT-x / AMD-V resolved it
- Memory virtualization: shadow page tables vs. Extended Page Tables (EPT)
- Linux containers: namespaces (pid, net, mnt, uts, ipc, user) and cgroups for resource limits
- Para-virtualization and the Xen hypercall interface
- When to choose VMs vs. containers in production deployments

## Recommended Resource

Search for "KVM/QEMU virtualization explained" or "Docker containers vs virtual machines" on YouTube. The freeCodeCamp channel and "Hussein Nasser" both have detailed video explanations of these topics.

## Reference Material

- OSTEP Appendix — Virtual Machines: https://pages.cs.wisc.edu/~remzi/OSTEP/
- MIT 6.828 Lecture 20 — Virtual Machines: https://ocw.mit.edu/courses/6-828-operating-system-engineering-fall-2012/
