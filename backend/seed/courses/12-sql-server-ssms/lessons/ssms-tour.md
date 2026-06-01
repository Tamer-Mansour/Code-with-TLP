# A Tour of SSMS

SQL Server Management Studio is the Swiss-army GUI for SQL Server. Download from `aka.ms/ssms`; it's free.

## Layout

When you connect to a server (Server name `localhost` or `(local)\SQLEXPRESS`, choose Windows or SQL Auth), you'll see:

- **Object Explorer** (left) — tree of Databases → Tables → Columns / Keys / Indexes.
- **Query window** (center) — the T-SQL editor where you'll spend most of your time.
- **Results / Messages pane** (bottom) — grid for query results, text for `PRINT` output and errors.

## Connecting

```
Server name: localhost
Authentication: Windows Authentication  (or SQL Server Auth + login/password)
```

For remote servers add the port: `myserver,1433`.

## Useful keyboard shortcuts

| Shortcut         | Action                                |
|------------------|---------------------------------------|
| `F5`             | Execute the selected text (or all)    |
| `Ctrl + L`       | Display the **estimated** plan        |
| `Ctrl + M`       | Toggle the **actual** plan capture    |
| `Ctrl + R`       | Hide/show the results pane            |
| `Ctrl + Shift + R` | Refresh IntelliSense cache          |
| `Ctrl + K, Ctrl + C` | Comment selection                 |
| `Ctrl + K, Ctrl + U` | Uncomment selection               |
| `Alt + drag`     | Block (column-mode) selection         |

## Running scripts

```sql
USE shop;
GO

SELECT TOP 10 * FROM dbo.users ORDER BY created_at DESC;
GO
```

**`GO` is not T-SQL** — it's an SSMS/`sqlcmd` batch separator. SSMS sends everything between `GO`s to the server as one batch.

## Object Explorer power moves

- Right-click a table → **Script Table as → CREATE/SELECT/INSERT** to scaffold T-SQL.
- Right-click a table → **Edit Top 200 Rows** for a spreadsheet-style editor (be careful in production).
- Right-click a database → **Tasks → Generate Scripts** to export schema + data.
- Drag a table from Object Explorer into a query window to drop its fully-qualified name.

## Query designer

For complex `SELECT`s, right-click in the query window → **Design Query in Editor**. It's a GUI join builder. Useful when learning; most pros write T-SQL directly.

## Activity Monitor

`Ctrl + Alt + A` opens Activity Monitor: current sessions, expensive queries, waits, recent IO. It's the *first* tool to open when "the server is slow."

## Saving and source control

A `.sql` file is just a script. Keep them in git. SSMS has no built-in source control beyond what Visual Studio integration provides; you'll usually live with `git add some-fix.sql` from a terminal.

## Light theme / dark theme

Tools → Options → Environment → General → Color Theme. (Dark theme arrived officially in SSMS 19.)
