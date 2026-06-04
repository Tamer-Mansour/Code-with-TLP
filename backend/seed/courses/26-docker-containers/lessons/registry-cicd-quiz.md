# Quiz: Registries and CI/CD

**Q1. The `latest` tag in Docker Hub:**
- [ ] Always points to the most recently published image version
- [ ] Is automatically updated when a newer image is pushed with any tag
- [x] Is just a conventional tag with no special behavior — it points to whatever was last tagged `latest`
- [ ] Is immutable once set

**Q2. In a CI pipeline, which tagging strategy gives you the most reproducible deployments?**
- [ ] Always tag images as `latest`
- [ ] Use the branch name as the tag
- [x] Tag images with the git commit SHA (e.g., `myapp:a3f9c21`)
- [ ] Use the build timestamp as the tag

**Q3. To push an image to Docker Hub as `myorg/myapp:2.1.0`, which commands are correct (in order)?**
- [ ] `docker tag myapp:2.1.0 myorg/myapp:2.1.0` then `docker push myapp:2.1.0`
- [x] `docker tag myapp:latest myorg/myapp:2.1.0` then `docker push myorg/myapp:2.1.0`
- [ ] `docker push myorg/myapp:2.1.0` (no tagging needed)
- [ ] `docker build -t myorg/myapp:2.1.0 --push .`

**Q4. Docker layer caching in CI (e.g., GitHub Actions) typically requires:**
- [ ] Nothing — CI agents share a persistent Docker cache automatically
- [x] Explicitly pulling a cache image or using BuildKit's `--cache-from` / `--cache-to` flags
- [ ] Setting `DOCKER_BUILDKIT=0` to enable caching
- [ ] Using only `RUN` instructions (no COPY)

**Q5. `EXPOSE 443` in a Dockerfile does which of the following in a CI pipeline?**
- [ ] Opens port 443 on the CI runner so integration tests can connect
- [ ] Publishes port 443 when the container starts during `docker run` in CI
- [x] Has no effect on port availability — it is documentation only
- [ ] Creates a TLS certificate for the container

**Q6. Which Docker command scans a local image for known CVEs?**
- [ ] `docker audit myapp:latest`
- [ ] `docker verify myapp:latest`
- [x] `docker scout cves myapp:latest`
- [ ] `docker security myapp:latest`

**Q7. A blue/green deployment with Docker means:**
- [ ] Running containers with `--color blue` or `--color green` flags
- [x] Maintaining two identical production environments; traffic switches to the new version after it passes health checks
- [ ] Using Docker Compose `blue` and `green` profile names
- [ ] Splitting traffic 50/50 between two container versions at all times

**Q8. When should you use a private container registry instead of Docker Hub public repos?**
- [ ] When your images are larger than 1 GB
- [ ] When you need multi-arch images
- [x] When your images contain proprietary code or secrets and should not be publicly accessible
- [ ] When you want faster pull speeds regardless of image content
