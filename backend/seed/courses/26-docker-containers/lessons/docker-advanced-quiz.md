# Quiz: Advanced Docker Topics

**Q1. A container exits with code 137. What most likely happened?**
- [ ] The application raised an unhandled exception
- [ ] The container was stopped with `docker stop`
- [x] The Linux OOM killer terminated the container process due to memory limit exceeded
- [ ] The health check failed too many times

**Q2. Which Compose option makes service `api` wait until service `db` is healthy before starting?**
- [ ] `links: [db]`
- [ ] `after: [db]`
- [x] `depends_on: db: condition: service_healthy`
- [ ] `requires: db`

**Q3. What does `HEALTHCHECK --start-period=30s` do?**
- [ ] Delays the first health check by 30 seconds after image build
- [x] Gives the container 30 seconds to start up before health check failures count
- [ ] Sets the timeout for each individual health check to 30 seconds
- [ ] Restarts the container after 30 seconds if unhealthy

**Q4. `--cpus 0.5` on a 4-core host means:**
- [ ] The container gets 50% of all 4 cores (2 full cores)
- [x] The container may use up to 50% of one CPU core
- [ ] The container is pinned to CPU core 0 at half speed
- [ ] The container shares CPU equally with all other containers

**Q5. Which tag strategy is safest for production deployments?**
- [ ] `myapp:latest`
- [ ] `myapp:stable`
- [x] `myapp:1.3.7` or `myapp:sha-a1b2c3d`
- [ ] `myapp:dev`

**Q6. What is the purpose of `docker system prune -a`?**
- [ ] Removes only stopped containers
- [ ] Removes only dangling (untagged) images
- [x] Removes all stopped containers, all unused images, unused networks, and build cache
- [ ] Removes running containers and their volumes
