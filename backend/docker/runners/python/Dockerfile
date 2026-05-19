FROM python:3.11-slim

# Lock down: non-root user, no apt cache.
RUN useradd -ms /bin/bash runner
WORKDIR /workspace
USER runner

# stdout buffering off so we don't lose output on a crash.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

CMD ["python", "-u", "/workspace/solution.py"]
