# Quiz: Node Basics

**Q1. Node's command-processing model is:**
- [ ] Multi-threaded by default
- [x] Single-threaded with a non-blocking event loop
- [ ] One thread per request
- [ ] Fork-per-request

**Q2. The recommended way to import a built-in module in modern Node is:**
- [ ] `require("fs")`
- [x] `import fs from "node:fs/promises"`
- [ ] `import { fs } from "node"`
- [ ] `node fs`

**Q3. Long synchronous work in a request handler:**
- [ ] Has no impact on other requests
- [x] Blocks the event loop and freezes other requests
- [ ] Auto-spawns a worker
- [ ] Triggers garbage collection

**Q4. Which is best for CPU-bound work in Node?**
- [ ] More setTimeout calls
- [ ] Promise chains
- [x] Worker Threads or a separate process
- [ ] More `process.nextTick`

**Q5. To enable ESM in a Node project you set in `package.json`:**
- [ ] `"esm": true`
- [x] `"type": "module"`
- [ ] `"moduleType": "es"`
- [ ] `"format": "esm"`

**Q6. Node's standard test runner is invoked with:**
- [ ] `node test`
- [x] `node --test`
- [ ] `npm test` (only, no built-in)
- [ ] `jest`
