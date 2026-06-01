# Installing MongoDB and mongosh

Three quick ways to get a server.

## 1. Docker

```bash
docker run --name mongo -d -p 27017:27017 mongo:7
```

Clean teardown: `docker stop mongo && docker rm mongo`.

## 2. Native install

- **macOS:** `brew tap mongodb/brew && brew install mongodb-community && brew services start mongodb-community`
- **Ubuntu:** follow the apt instructions at `mongodb.com/docs/manual/installation/`
- **Windows:** download the MSI and let it install as a service.

## 3. MongoDB Atlas

The hosted service. Free M0 tier for learning. You'll get a connection string like:

```
mongodb+srv://user:pass@cluster0.abcd.mongodb.net
```

## Connecting with mongosh

```bash
mongosh "mongodb://localhost:27017"
```

You'll see:

```
test>
```

The default database is called `test`. Switch with `use`:

```javascript
use shop
```

## First commands

```javascript
db.users.insertOne({ name: "Alice", email: "alice@example.com" });
db.users.find();
db.users.countDocuments();
```

`db` refers to the current database; the property name after `db` is the **collection** (a "table" of documents). Collections appear on first write — you don't `CREATE COLLECTION` explicitly.

## The shell is JavaScript

`mongosh` is a real JS REPL. You can write:

```javascript
const recent = db.orders.find({ createdAt: { $gte: new Date("2025-01-01") } }).toArray();
console.log(`${recent.length} recent orders`);
recent.filter(o => o.total > 100).forEach(o => print(o._id));
```

That makes light scripting trivial.

## Useful shell helpers

| Command                              | What it does                          |
|--------------------------------------|---------------------------------------|
| `show dbs`                           | List databases                        |
| `show collections`                   | List collections in current db        |
| `db.coll.stats()`                    | Storage stats                         |
| `db.coll.getIndexes()`               | Indexes on `coll`                     |
| `db.coll.find().pretty()`            | Pretty-printed results                |
| `db.serverStatus()`                  | Server health and counters            |

## Compass — the GUI

MongoDB Compass is the official desktop client. Free. Better than the shell for browsing data, building queries with autocomplete, and visualizing schemas. Download from `mongodb.com/products/compass`.

## Connection string anatomy

```
mongodb://user:pass@host:27017/dbname?replicaSet=rs0&readPreference=primary&tls=true
```

You'll feed this to your application driver. The `+srv` form (DNS-based) is preferred for managed clusters — it discovers all replicas via SRV records.
