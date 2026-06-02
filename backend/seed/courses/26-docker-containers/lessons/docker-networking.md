# Docker Networking

Docker containers communicate through **virtual networks** managed by the Docker daemon. Understanding networking is essential when running multi-container applications.

## Default Networks

Docker ships with three built-in networks:

| Network   | Driver  | Purpose                                      |
|-----------|---------|----------------------------------------------|
| `bridge`  | bridge  | Default for standalone containers            |
| `host`    | host    | Shares the host network namespace (Linux)    |
| `none`    | null    | No networking at all                         |

List them with:

```bash
docker network ls
```

## The Bridge Network

When you run `docker run myapp`, Docker connects it to the default `bridge` network and assigns a private IP (usually `172.17.0.x`). Containers on the same bridge can reach each other by IP, but **not by name** — DNS resolution between containers only works on **user-defined** bridge networks.

## User-Defined Bridge Networks

Create a named network so containers can find each other by service name:

```bash
docker network create mynet

docker run -d --name db --network mynet postgres:16
docker run -d --name api --network mynet myapi:latest
```

Now `api` can connect to `db:5432` — Docker's embedded DNS resolves `db` to the container's IP automatically.

## Inspecting Networks

```bash
docker network inspect mynet
```

This prints all connected containers, their IPs, and network configuration as JSON.

## Port Publishing

Containers have internal ports. To reach them from the host (or the outside world) you must **publish** the port:

```bash
docker run -d -p 8080:3000 myapp
#              ^host ^container
```

Multiple containers can each expose port 3000 internally; the host port (`8080`) must be unique.

## Port Publishing vs EXPOSE

`EXPOSE 3000` in a Dockerfile is **documentation only** — it tells readers and tooling which port the app listens on. It does *not* publish the port. You must still pass `-p` at runtime.

## Host Network (Linux Only)

```bash
docker run --network host nginx
```

The container shares the host's network namespace — no NAT, no port mapping. Useful for high-performance workloads or when you need to sniff the network. Not available on Docker Desktop for Mac/Windows.

## Network Aliases

A container can be reachable under multiple names on the same network:

```bash
docker run -d --network mynet --network-alias cache redis:7
```

Other containers on `mynet` can connect to `cache:6379`.

## Overlay Networks (Swarm / Kubernetes)

For multi-host deployments, Docker Swarm uses **overlay networks** that span hosts via VXLAN tunnels. Kubernetes uses a CNI plugin (Flannel, Calico, Cilium) instead of Docker networking. These are beyond the scope of this course but follow the same mental model.

## Quick Reference

```bash
docker network create mynet
docker network ls
docker network inspect mynet
docker network connect mynet mycontainer
docker network disconnect mynet mycontainer
docker network rm mynet
```

Understanding networks lets you confidently wire together databases, caches, APIs, and reverse proxies all within Docker — and reproduce that setup in production with Docker Compose or Kubernetes.
