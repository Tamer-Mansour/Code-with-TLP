# The Node Runtime and Event Loop

Node.js is JavaScript outside the browser, with bindings to OS primitives — files, networking, child processes, timers. The runtime is **single-threaded** but handles thousands of concurrent connections via a non-blocking event loop.

## Install

```bash
# macOS
brew install node
# Linux: nodesource or distro
# Windows: msi installer or winget

node --version
npm --version
```

Or use a version manager: **fnm** (fast) or **volta**.

## Hello, Node

`server.js`:

```js
import http from "node:http";

const server = http.createServer((req, res) => {
  res.writeHead(200, { "Content-Type": "text/plain" });
  res.end("hello\n");
});

server.listen(3000, () => console.log("listening on :3000"));
```

```bash
node server.js
```

`node:` prefix marks built-in modules — works in both ESM and CJS, makes intent explicit.

## The event loop

Node uses **libuv**. Per tick:

```
timers   → setTimeout/setInterval callbacks
pending  → some I/O callbacks
poll     → wait for new I/O
check    → setImmediate callbacks
close    → 'close' event callbacks
```

Between phases, microtasks drain: `process.nextTick` first, then promises.

The takeaway: **don't block the event loop**. Long synchronous work freezes every connection. Move CPU-heavy work to a **Worker Thread** or a separate process.

## ESM vs CommonJS

Modern Node supports both:

```js
// ESM (recommended)
import fs from "node:fs/promises";
const data = await fs.readFile("file.txt", "utf8");

// CommonJS (legacy)
const fs = require("fs/promises");
```

Enable ESM in `package.json`:

```json
{ "type": "module" }
```

Most new projects use ESM. The ecosystem has caught up.

## package.json scripts

```json
{
  "type": "module",
  "scripts": {
    "dev": "node --watch server.js",
    "start": "node server.js",
    "test": "node --test"
  }
}
```

`node --watch` restarts on file changes. `node --test` runs the built-in test runner (no Jest required for simple cases).

## Streams

Node's I/O is built on streams. `req` and `res` in HTTP are streams; so are file reads, gzip pipes, network sockets.

```js
import { createReadStream, createWriteStream } from "node:fs";
import { createGzip } from "node:zlib";

await pipeline(
  createReadStream("input.txt"),
  createGzip(),
  createWriteStream("input.txt.gz")
);
```

`pipeline` connects streams and handles errors and cleanup automatically.

## Worker Threads — actual parallelism

```js
import { Worker } from "node:worker_threads";

const worker = new Worker("./heavy.js", { workerData: { input: ... } });
worker.on("message", result => ...);
```

For CPU-bound work. The worker runs on its own OS thread.

## What Node is good for

- HTTP APIs (huge ecosystem).
- Real-time servers (WebSockets, SSE).
- CLI tools.
- Build tooling (Vite, Webpack, esbuild).
- Glue scripts.

What it's not great for: CPU-bound number crunching, ML inference (use Python or native bindings), low-level systems.
