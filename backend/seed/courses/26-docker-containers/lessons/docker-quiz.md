# Quiz: Docker Basics

**Q1. Containers share what with the host?**
- [ ] The user's home directory
- [x] The kernel
- [ ] All open ports
- [ ] The GPU by default

**Q2. The unit of distribution in Docker is:**
- [ ] A container
- [x] An image
- [ ] A snapshot
- [ ] A volume

**Q3. To publish container port 80 on host port 8080 you use:**
- [ ] `-e 8080:80`
- [ ] `-v 8080:80`
- [x] `-p 8080:80`
- [ ] `-net 8080:80`

**Q4. The instruction in a Dockerfile that almost never changes (so it caches well) is:**
- [x] The `FROM` line
- [ ] The last `RUN`
- [ ] `CMD`
- [ ] `ENV`

**Q5. To make data survive container deletion you use:**
- [ ] A bigger image
- [x] A volume (named or bind mount)
- [ ] `--persist`
- [ ] A separate registry

**Q6. The shortcut to remove all stopped containers and unused images is:**
- [ ] `docker rm all`
- [x] `docker system prune -a`
- [ ] `docker clean`
- [ ] `docker reset`
