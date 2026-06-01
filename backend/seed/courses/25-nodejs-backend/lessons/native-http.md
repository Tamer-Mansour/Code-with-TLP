# Native http and JSON

Before reaching for Express, look at what Node's built-in `node:http` does. For simple services it's enough — and it teaches the shape of every Node framework.

## A JSON echo server

```js
import http from "node:http";

const server = http.createServer(async (req, res) => {
  if (req.method !== "POST") {
    res.writeHead(405, { "Content-Type": "text/plain" });
    return res.end("method not allowed\n");
  }

  const chunks = [];
  for await (const chunk of req) chunks.push(chunk);
  const body = Buffer.concat(chunks).toString("utf8");

  let data;
  try { data = JSON.parse(body); }
  catch (e) {
    res.writeHead(400, { "Content-Type": "application/json" });
    return res.end(JSON.stringify({ error: "bad json" }));
  }

  res.writeHead(200, { "Content-Type": "application/json" });
  res.end(JSON.stringify({ received: data }));
});

server.listen(3000);
```

## Routing by URL

```js
import { URL } from "node:url";

const server = http.createServer((req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);
  const path = url.pathname;

  if (req.method === "GET" && path === "/health") {
    return res.end(JSON.stringify({ ok: true }));
  }

  if (req.method === "GET" && path.startsWith("/users/")) {
    const id = path.slice("/users/".length);
    return res.end(JSON.stringify({ id }));
  }

  res.writeHead(404);
  res.end();
});
```

Once you write the second `if`, you want a router. That's why Express exists.

## Streaming responses

`res` is a writable stream:

```js
res.writeHead(200, { "Content-Type": "application/json" });
const stream = getUsersStream();        // some readable stream
stream.pipe(res);
```

For Server-Sent Events:

```js
res.writeHead(200, {
  "Content-Type": "text/event-stream",
  "Cache-Control": "no-cache",
  Connection: "keep-alive",
});
setInterval(() => res.write(`data: ${Date.now()}\n\n`), 1000);
```

## fetch (the client)

Node 18+ ships a global `fetch`:

```js
const r = await fetch("https://api.github.com/users/octocat");
const data = await r.json();
```

For HTTP clients in newer Node, you rarely need `axios` or `got` anymore.

## AbortController

Cancel any I/O — works with `fetch`, file reads, network sockets:

```js
const ac = new AbortController();
setTimeout(() => ac.abort(), 3000);

const r = await fetch(url, { signal: ac.signal });
```

## Graceful shutdown

A production-quality server stops accepting new connections, lets in-flight finish, then exits:

```js
process.on("SIGTERM", () => {
  server.close(() => {
    db.close().then(() => process.exit(0));
  });
});
```

Kubernetes/Docker send SIGTERM; handle it or lose requests.

## When native is enough

Tiny services (health endpoint, webhook receiver, status page) genuinely don't need a framework. For anything routing-heavy or middleware-driven, move to Express/Fastify.
