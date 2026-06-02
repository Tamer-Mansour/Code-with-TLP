# Full-Text Search with tsvector and tsquery

PostgreSQL ships with a built-in full-text search (FTS) engine — no external search service required for moderate workloads. It uses two types: `tsvector` (a pre-processed, sorted list of lexemes) and `tsquery` (a search expression).

## Core concepts

| Type       | Holds                               | Example value                           |
|------------|-------------------------------------|-----------------------------------------|
| `tsvector` | Normalized, weighted lexemes        | `'cat':3 'quick':1 'run':2`            |
| `tsquery`  | A boolean search expression         | `'quick' & 'cat'`                      |

Postgres converts free text to a `tsvector` using `to_tsvector(config, text)`, and user input to a `tsquery` with `to_tsquery` or the friendlier `plainto_tsquery` / `websearch_to_tsquery`.

## Creating a search-ready column

```sql
-- Add a generated tsvector column (Postgres 12+)
ALTER TABLE articles
  ADD COLUMN search_vector tsvector
    GENERATED ALWAYS AS (
      to_tsvector('english', coalesce(title, '') || ' ' || coalesce(body, ''))
    ) STORED;

-- Index it for fast search
CREATE INDEX ix_articles_fts ON articles USING GIN (search_vector);
```

The `'english'` text search configuration handles English stop words, stemming (`running` → `run`), and casing.

## Querying

```sql
-- Boolean AND (both words must appear)
SELECT title
FROM articles
WHERE search_vector @@ to_tsquery('english', 'postgresql & index');

-- Phrase search (words adjacent, in order)
SELECT title
FROM articles
WHERE search_vector @@ phraseto_tsquery('english', 'query planner');

-- Web-style input (handles AND / OR / minus)
SELECT title
FROM articles
WHERE search_vector @@ websearch_to_tsquery('english', 'postgres -mysql');
```

The `@@` operator returns `true` when the vector matches the query.

## Ranking results

```sql
SELECT title,
       ts_rank(search_vector, query) AS rank
FROM articles,
     to_tsquery('english', 'postgres & performance') AS query
WHERE search_vector @@ query
ORDER BY rank DESC
LIMIT 20;
```

`ts_rank` scores by term frequency. `ts_rank_cd` uses cover-density scoring (rewards matches that are close together).

## Highlighting matches

```sql
SELECT ts_headline(
  'english',
  body,
  to_tsquery('english', 'index'),
  'StartSel=<b>, StopSel=</b>, MaxWords=15, MinWords=5'
)
FROM articles
WHERE search_vector @@ to_tsquery('english', 'index');
```

`ts_headline` wraps matched terms in your chosen markup — useful for search result previews.

## Multi-column search with weights

Assign weights (A > B > C > D) to give the title more influence than the body:

```sql
to_tsvector('english', coalesce(title, '')) ||
setweight(to_tsvector('english', coalesce(body, '')), 'B')
```

Prefix the title vector with no `setweight` call (default weight A), and mark the body B.

## When to upgrade to a dedicated search engine

Full-text search in Postgres works well up to tens of millions of rows with modest search volume. Consider Elasticsearch or Typesense when you need fuzzy matching on typos, multi-language tokenizers beyond what Postgres text-search configs offer, or sub-100ms search at hundreds of queries per second on billions of documents.
