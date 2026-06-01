# A Tour of the mysql Shell

The `mysql` CLI is more than a query window. A handful of commands make day-to-day work much faster.

## Statements vs. client commands

- A **SQL statement** ends with `;` and is sent to the server.
- A **client command** starts with `\` (or a word like `help`) and is interpreted locally.

```sql
-- a statement
SELECT NOW();
```

```
\s     -- client: print connection status
```

## Tab completion and history

The shell remembers everything you typed (in `~/.mysql_history`). Up-arrow walks history. Tab completes table and column names if you started with `--auto-rehash` (the default).

## Running a script

```bash
mysql -u root -p shop < seed.sql
```

Or interactively:

```
mysql> source /tmp/seed.sql
```

## Pretty output for wide tables

`\G` ends a statement and renders the result vertically — one column per line. Great for tables with many columns:

```sql
SELECT * FROM users WHERE id = 1\G
```

## Edit your last query

`\e` opens the previous statement in your `$EDITOR`. Save and exit and it runs.

## Limiting output safely

Always `LIMIT` exploratory queries on big tables:

```sql
SELECT * FROM events LIMIT 10;
```

Otherwise you'll wait while the server streams millions of rows.

## Useful one-liners

| Command                                  | What it shows                |
|------------------------------------------|------------------------------|
| `SHOW DATABASES;`                        | All databases                |
| `SHOW TABLES;`                           | Tables in current DB         |
| `DESCRIBE users;`                        | Columns + types of `users`   |
| `SHOW CREATE TABLE users\G`              | Full DDL of a table          |
| `SHOW INDEX FROM users;`                 | Indexes on a table           |
| `SHOW PROCESSLIST;`                      | Active connections + queries |
| `SELECT VERSION();`                      | Server version               |

## Safer defaults

Run with `--safe-updates` (alias `-U`). It refuses `UPDATE` and `DELETE` that don't have a `WHERE` clause or `LIMIT`. You'll be grateful the first time it saves you.

```bash
mysql -u root -p -U shop
```

## Exiting

`\q`, `exit`, `quit`, or Ctrl-D. All four work.
