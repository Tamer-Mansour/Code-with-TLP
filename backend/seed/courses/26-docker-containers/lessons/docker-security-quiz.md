# Quiz: Docker Security

**Q1. What is the primary risk of running a container as root?**
- [ ] The container starts slower
- [ ] The container cannot bind ports below 1024
- [x] A compromised process may escalate to root on the host via kernel exploits
- [ ] Docker will refuse to start the container

**Q2. Which flag makes the container's root filesystem read-only?**
- [ ] `--no-write`
- [ ] `--immutable`
- [x] `--read-only`
- [ ] `--ro-root`

**Q3. Why should you never mount `/var/run/docker.sock` into a production container?**
- [ ] It is a large file and wastes disk space
- [ ] It causes performance degradation
- [x] It gives the container full control over the Docker daemon — equivalent to host root
- [ ] Docker Compose does not support socket mounts

**Q4. Which of the following correctly pins an image to a specific immutable version?**
- [ ] `FROM node:20-latest`
- [ ] `FROM node:20`
- [x] `FROM node:20@sha256:abc123...`
- [ ] `FROM node:20-stable`

**Q5. The `--cap-drop ALL` flag does what?**
- [ ] Drops all environment variables from the container
- [ ] Removes the container's network interface
- [x] Removes all Linux capabilities from the container process
- [ ] Deletes all Docker images on the host

**Q6. Which is the safest base image choice for a compiled Go binary with no runtime dependencies?**
- [ ] `ubuntu:22.04`
- [ ] `node:20-alpine`
- [x] `gcr.io/distroless/static:nonroot`
- [ ] `python:3.12-slim`
