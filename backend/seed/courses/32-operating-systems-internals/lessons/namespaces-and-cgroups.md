# Namespaces and cgroups: How Containers Isolate

Containers are not a single kernel feature — they are built from two orthogonal Linux primitives: **namespaces** for visibility isolation and **cgroups** for resource control. Together they create the illusion of a private machine.

## Namespaces: What Can You See?

A namespace wraps a global resource so that processes in the namespace see their own isolated view of it. Linux 6.x provides eight namespace types:

| Namespace | Flag | What is isolated |
|---|---|---|
| **Mount** (`mnt`) | `CLONE_NEWNS` | Filesystem mount points |
| **PID** | `CLONE_NEWPID` | Process ID number space |
| **Network** (`net`) | `CLONE_NEWNET` | Network interfaces, routing tables, ports |
| **IPC** | `CLONE_NEWIPC` | SysV IPC, POSIX message queues |
| **UTS** | `CLONE_NEWUTS` | Hostname and domain name |
| **User** | `CLONE_NEWUSER` | UID/GID mappings (root inside = non-root outside) |
| **Cgroup** | `CLONE_NEWCGROUP` | cgroup root (hides host cgroup hierarchy) |
| **Time** | `CLONE_NEWTIME` | Monotonic and boot clocks |

### Creating a Namespace

```c
#include <sched.h>
#include <unistd.h>

int main(void) {
    /* Create new PID + network + mount namespace */
    if (unshare(CLONE_NEWPID | CLONE_NEWNET | CLONE_NEWNS) < 0) {
        perror("unshare"); return 1;
    }
    /* From here, this process has PID 1 in the new namespace */
    execl("/bin/sh", "sh", NULL);
}
```

```bash
# See namespaces for a process
ls -la /proc/self/ns/

# Run a shell in a new network namespace (no network access)
unshare --net /bin/bash
ip link    # only loopback visible
```

### PID Namespace Deep Dive

```
Host:  PID 1 (systemd)  PID 1234 (containerd)  PID 5678 (container init)
                                                        │
Container namespace:                             PID 1 (container init)
                                                 PID 2 (nginx)
```

The container's `init` process has PID 1 **inside** the namespace. From the host it has PID 5678. A `kill -9 1` inside the container kills only the container's init, not the host's systemd.

## cgroups: How Much Can You Use?

**Control groups (cgroups)** limit, account for, and isolate the resource usage of groups of processes. Cgroups v2 (unified hierarchy, Linux 4.5+, default since Ubuntu 22.04) exposes a single filesystem tree at `/sys/fs/cgroup/`.

### Resource Controllers

| Controller | Controls |
|---|---|
| `cpu` | CPU bandwidth (weight, quota) |
| `memory` | RAM + swap limits, OOM behavior |
| `io` | Block I/O weight, rate limits |
| `pids` | Maximum number of processes |
| `cpuset` | Allowed CPU cores and NUMA nodes |
| `net_cls` / `net_prio` | Network packet classification |

### Setting a Memory Limit

```bash
# Create a cgroup for a container
mkdir /sys/fs/cgroup/mycontainer

# Set 256 MB memory limit
echo $((256 * 1024 * 1024)) > /sys/fs/cgroup/mycontainer/memory.max

# Set CPU quota: 50% of one core (50000 us per 100000 us period)
echo "50000 100000" > /sys/fs/cgroup/mycontainer/cpu.max

# Add a PID to the cgroup
echo 9999 > /sys/fs/cgroup/mycontainer/cgroup.procs
```

### OOM Killer in Cgroups

If a cgroup exceeds its `memory.max`, the kernel's OOM killer selects a process **within that cgroup** to kill, not a random process on the host. This is crucial for container isolation.

## How Docker/containerd Uses These

```
docker run --memory=256m --cpus=0.5 ubuntu bash
```

Internally, the container runtime:

1. Calls `clone()` with namespace flags to create a new PID/net/mnt/UTS namespace.
2. Creates a cgroup hierarchy entry under `/sys/fs/cgroup/<runtime>/<container-id>/`.
3. Writes memory and CPU limits to cgroup files.
4. Sets up a `pivot_root` or `chroot` inside the mount namespace (the container's root filesystem).
5. Drops capabilities (`CAP_SYS_ADMIN` etc.) and applies a seccomp filter.
6. Executes the container's entrypoint.

## Namespaces vs. cgroups — Summary

| | Namespaces | cgroups |
|---|---|---|
| Purpose | Visibility — what you can see | Accounting — how much you can use |
| Key syscalls | `clone()`, `unshare()`, `setns()` | cgroup fs (`/sys/fs/cgroup/`) |
| Prevents | Seeing other containers' processes | Using more CPU/RAM than allocated |
| Does NOT prevent | Using infinite CPU (without cgroups) | Seeing other processes (without ns) |

## Common Pitfall

Namespaces alone do not limit resource consumption. A container with a PID namespace but no cgroup can fork-bomb the host. Always pair them. Similarly, cgroups without namespaces limit resources but don't hide host processes — the container could still see (and potentially signal) other workloads.

> **Interview answer:** "Namespaces give each container an isolated view of PIDs, network, mounts, and users. cgroups enforce CPU, memory, and I/O limits. Together they form the isolation primitive Linux container runtimes (Docker, containerd, CRI-O) build on. Neither is sufficient alone — namespaces hide; cgroups constrain."
