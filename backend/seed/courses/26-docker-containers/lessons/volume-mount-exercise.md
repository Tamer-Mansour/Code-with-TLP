# Exercise: Parse Docker Volume Mounts

Given a list of Docker volume mount strings (as passed to `-v`), classify each as a **named volume**, **bind mount**, or **tmpfs** (anonymous in-memory), then count each type.

A mount string follows these rules:
- **Named volume**: starts with a word character (letter, digit, underscore, dash) and contains no `/` before the first colon (e.g. `pgdata:/var/lib/postgresql/data`).
- **Bind mount**: starts with `/` or `./` or `../` (an absolute or relative host path), e.g. `./src:/app/src` or `/home/dev:/home/dev`.
- **Anonymous volume**: a single path with no colon and no leading `/`, e.g. `/app/node_modules` — treated as anonymous/tmpfs for this exercise.

Read the mounts from stdin and print three lines: `named=N`, `bind=N`, `anonymous=N`.
