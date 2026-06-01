# A Tour of psql

`psql` is Postgres's interactive shell — and one of the best CLI database clients ever shipped.

## Connecting

```bash
psql -h localhost -U postgres -d mydb
psql "postgresql://user:pass@host:5432/mydb"
```

Set defaults in `~/.pgpass` to skip the password prompt:

```
host:port:database:user:password
```

(chmod 600 it.)

## Meta-commands

Anything starting with `\` is a **meta-command** — interpreted by psql, not the server. Some of the most useful:

| Command           | What it does                          |
|-------------------|---------------------------------------|
| `\l`              | list databases                        |
| `\c mydb`         | connect to database mydb              |
| `\dt`             | list tables                           |
| `\dt+`            | list tables with sizes                |
| `\d users`        | describe table `users`                |
| `\d+ users`       | describe with column stats            |
| `\di`             | list indexes                          |
| `\df`             | list functions                        |
| `\du`             | list users/roles                      |
| `\dn`             | list schemas                          |
| `\sf func_name`   | show source of a function             |
| `\timing`         | toggle timing each query              |
| `\watch 2`        | re-run last query every 2 seconds     |
| `\e`              | edit last query in `$EDITOR`          |
| `\i file.sql`     | run a script                          |
| `\copy ... `      | client-side COPY for CSVs             |
| `\?` / `\h`       | help                                  |

`\d` is the killer feature. `\d+ orders` shows columns, types, indexes, foreign keys, triggers, and row size estimates in one screen.

## Expanded output

For wide tables:

```sql
\x          -- toggle expanded
SELECT * FROM users LIMIT 1;
```

You'll get a vertical rendering — one column per line.

## Copying data

The fastest way to load a CSV:

```sql
\copy users(id, email) FROM '/tmp/users.csv' CSV HEADER;
```

Server-side `COPY` is even faster, but requires the file to be readable by the Postgres user.

## Customizing your prompt

`~/.psqlrc`:

```
\set PROMPT1 '%[%033[1;33m%]%n@%/%R%[%033[0m%]%# '
\set HISTSIZE 5000
\timing on
\x auto
```

## Output formats

```sql
\pset format aligned     -- default
\pset format wrapped     -- wraps long fields
\pset format csv         -- CSV
\pset format html        -- HTML table
\pset null '(null)'      -- show NULLs distinctly
```

## Variables

```sql
\set userid 42
SELECT * FROM users WHERE id = :userid;
```

## Quitting

`\q`, `exit`, or Ctrl-D.
