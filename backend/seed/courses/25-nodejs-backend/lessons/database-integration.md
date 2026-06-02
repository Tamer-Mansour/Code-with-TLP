# Database Integration — PostgreSQL with node-postgres

Most production Node APIs need a relational database. This lesson uses **PostgreSQL** with the `pg` (node-postgres) driver — the lowest-overhead, most flexible choice for Node + Postgres.

## Install

```bash
npm install pg
```

## Connection Pool

Always use a pool — it reuses TCP connections instead of opening a new one per query:

```js
// db/pool.js
import pg from "pg";
const { Pool } = pg;

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 10,              // max simultaneous connections
  idleTimeoutMillis: 30_000,
  connectionTimeoutMillis: 2_000,
});

// Test connection on startup
pool.on("error", (err) => {
  console.error("Unexpected DB pool error", err);
  process.exit(1);
});

export default pool;
```

`DATABASE_URL` format: `postgresql://user:password@host:5432/dbname?sslmode=require`

## Running Queries

```js
import pool from "./db/pool.js";

// Simple query
const { rows } = await pool.query("SELECT * FROM users WHERE id = $1", [userId]);
const user = rows[0];   // undefined if not found

// Parameterized insert with RETURNING
const { rows: [created] } = await pool.query(
  "INSERT INTO users (name, email) VALUES ($1, $2) RETURNING *",
  [name, email]
);
```

Always use **parameterized queries** (`$1`, `$2`, ...). Never interpolate user input into SQL strings — that is a SQL injection vulnerability.

## Transactions

```js
const client = await pool.connect();
try {
  await client.query("BEGIN");

  const { rows: [order] } = await client.query(
    "INSERT INTO orders (user_id, total) VALUES ($1, $2) RETURNING id",
    [userId, total]
  );

  await client.query(
    "UPDATE inventory SET stock = stock - $1 WHERE product_id = $2",
    [quantity, productId]
  );

  await client.query("COMMIT");
  return order;
} catch (err) {
  await client.query("ROLLBACK");
  throw err;
} finally {
  client.release();    // always release back to pool
}
```

## ORM Alternative — Prisma

If you prefer a schema-driven approach with auto-generated types:

```bash
npm install prisma --save-dev
npm install @prisma/client
npx prisma init
```

```prisma
// prisma/schema.prisma
model User {
  id        Int      @id @default(autoincrement())
  name      String
  email     String   @unique
  createdAt DateTime @default(now())
  posts     Post[]
}
```

```js
import { PrismaClient } from "@prisma/client";
const prisma = new PrismaClient();

const user = await prisma.user.findUnique({ where: { email } });
const users = await prisma.user.findMany({ where: { role: "admin" } });
```

## Comparison: Raw pg vs Prisma

| | `pg` (raw) | Prisma |
|--|-----------|--------|
| Setup | Minimal | Schema + migration tooling |
| Type safety | Manual | Auto-generated |
| Flexibility | Full SQL | Good for CRUD, raw SQL for complex |
| Performance | Maximum | Slightly more overhead |
| Learning curve | Low | Medium |

Use `pg` for simple services or when you need full SQL control. Use Prisma when you want a typed schema and automated migrations.

## Migrations

Never change a production schema manually. Use a migration tool:

- **Prisma Migrate** — `npx prisma migrate dev`
- **node-pg-migrate** — plain SQL files, more control
- **Flyway / Liquibase** — enterprise-grade, polyglot

Each migration is a versioned SQL file committed to your repo and run in CI before deploy.

## Environment Configuration

```bash
# .env (never commit this file)
DATABASE_URL=postgresql://api_user:secretpass@localhost:5432/mydb
```

Validate on startup:

```js
if (!process.env.DATABASE_URL) {
  throw new Error("DATABASE_URL environment variable is required");
}
```
