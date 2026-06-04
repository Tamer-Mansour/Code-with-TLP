# Exercise: Image Layer Size Calculator

Deepen your understanding of Docker's union filesystem by computing exactly how much disk space an image occupies and how much of that is actually usable in the running container.

## Background

Docker images are a stack of **read-only layers**. Each layer records file operations: additions, modifications, and deletions. Here is the crucial detail that surprises most beginners:

> **Deleting a file in a higher layer does NOT free the space used by that file in a lower layer.**

When a file is modified, OverlayFS copies the entire file up to the new layer (copy-on-write). The original copy remains in the lower layer forever. When a file is deleted, Docker adds a **whiteout marker** — a special file that hides the lower-layer version — but the original bytes stay on disk.

This is why:

```dockerfile
RUN apt-get update && apt-get install -y build-essential   # layer 2: +300 MB
RUN rm -rf /var/lib/apt/lists/*                            # layer 3: adds whiteout markers
```

The image is still ~300 MB larger than it would be without the cache. The fix is to chain the commands in one `RUN`:

```dockerfile
RUN apt-get update \
 && apt-get install -y build-essential \
 && rm -rf /var/lib/apt/lists/*      # same layer: deletion is free
```

Or use **multi-stage builds** so the build layer never enters the final image at all.

## Two Metrics

This exercise asks you to compute both:

1. **Total image size on disk**: the sum of bytes written across all layers (includes all modifications and original copies kept by copy-on-write).
2. **Effective filesystem size**: the bytes visible in a running container (topmost version of each surviving file only; deleted files count 0).

## Further Reading

- **The Docker Handbook** by Farhan Hasin Chowdhury: covers union filesystems and layer mechanics. Free at [https://github.com/fhsinchy/the-docker-handbook](https://github.com/fhsinchy/the-docker-handbook)
- **Docker Official Documentation**: [https://docs.docker.com/get-started/](https://docs.docker.com/get-started/)
