# Deploying Node.js APIs

A great API that cannot be reliably deployed and operated is worthless in production. This lesson covers the core practices for shipping Node services: process management, environment configuration, health checks, and containerisation.

## Running Node in Production

Never run `node server.js` directly in production without a process manager. If the process crashes, it stays down.

### PM2

PM2 is a popular Node process manager with automatic restarts, clustering, and log rotation:

```bash
npm install -g pm2

# Start
pm2 start src/server.js --name my-api

# Cluster mode — one process per CPU core
pm2 start src/server.js -i max --name my-api

# Auto-restart on crash, restart on file changes in dev
pm2 start src/server.js --watch

# Save process list and generate startup script
pm2 save
pm2 startup

# Logs
pm2 logs my-api
pm2 monit
```

### systemd (Linux)

For production VMs, systemd restarts the process and integrates with the OS:

```ini
# /etc/systemd/system/my-api.service
[Unit]
Description=My API
After=network.target

[Service]
Type=simple
User=nodeapp
WorkingDirectory=/opt/my-api
ExecStart=/usr/bin/node src/server.js
Restart=always
RestartSec=5
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
```

```bash
systemctl enable my-api
systemctl start my-api
systemctl status my-api
```

## Containerisation with Docker

Docker is the standard packaging format for cloud deployment:

```dockerfile
# Dockerfile
FROM node:22-alpine AS base
WORKDIR /app

# Install dependencies first (layer cached unless package*.json changes)
COPY package*.json ./
RUN npm ci --omit=dev

COPY . .

EXPOSE 3000
# Run as non-root user
USER node
CMD ["node", "src/server.js"]
```

```bash
docker build -t my-api:latest .
docker run -p 3000:3000 --env-file .env my-api:latest
```

Important Docker practices:
- Use `node:22-alpine` for small images (~150 MB vs ~900 MB for full Debian).
- Use `npm ci` (not `npm install`) in Docker — it respects the lockfile exactly.
- Run as a non-root user for security.
- Copy `package*.json` before source so dependency layer is cached between code changes.

## Health Check Endpoint

Every service needs a `/health` endpoint for load balancers and orchestrators:

```js
app.get("/health", async (req, res) => {
  try {
    await pool.query("SELECT 1");   // confirm DB is reachable
    res.json({ status: "ok", uptime: process.uptime() });
  } catch (err) {
    res.status(503).json({ status: "error", error: err.message });
  }
});
```

Return `200` when healthy, `503` when not. Keep it fast — no heavy computation.

## Graceful Shutdown

When the process receives SIGTERM (from a container orchestrator or PM2), finish in-flight requests before exiting:

```js
const server = app.listen(3000);

async function shutdown() {
  console.log("Shutting down...");
  server.close(async () => {
    await pool.end();              // close DB pool
    process.exit(0);
  });

  // Force exit if shutdown takes too long
  setTimeout(() => process.exit(1), 10_000);
}

process.on("SIGTERM", shutdown);
process.on("SIGINT", shutdown);
```

## Environment Configuration

| Variable | Description |
|----------|------------|
| `NODE_ENV` | `production` / `development` |
| `PORT` | HTTP port (default 3000) |
| `DATABASE_URL` | PostgreSQL connection string |
| `JWT_SECRET` | Secret for JWT signing |
| `LOG_LEVEL` | Pino log level (`info` in prod) |

Read `process.env.PORT` and fall back to a default:

```js
const PORT = parseInt(process.env.PORT ?? "3000", 10);
server.listen(PORT, () => logger.info(`Listening on :${PORT}`));
```

## Cloud Platforms

| Platform | Strengths |
|---------|-----------|
| **Railway** | Simple deploy from git, managed Postgres |
| **Render** | Free tier, auto-deploys |
| **Fly.io** | Docker-native, global edge |
| **AWS ECS/EKS** | Enterprise scale, steep learning curve |
| **Heroku** | Pioneer of PaaS, mature ecosystem |

Start with Railway or Render for side projects; move to AWS/GCP/Azure for enterprise workloads.

## Checklist

- [ ] Process managed by PM2 or systemd (or container orchestrator).
- [ ] `/health` endpoint returns 200 / 503.
- [ ] Graceful shutdown handles SIGTERM.
- [ ] Secrets in environment variables, not source code.
- [ ] `NODE_ENV=production` disables debug output and dev tools.
- [ ] Docker image uses non-root user and `npm ci`.
