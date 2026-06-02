# Full-Text Search in MongoDB

MongoDB provides a built-in **text index** type that lets you perform full-text searches on string fields. It handles tokenization, stemming, stop-word removal, and relevance scoring.

## Creating a Text Index

```javascript
// Index a single field
db.articles.createIndex({ body: "text" });

// Index multiple fields with weights
db.articles.createIndex(
  { title: "text", body: "text", tags: "text" },
  { weights: { title: 10, tags: 5, body: 1 }, name: "article_fulltext" }
);
```

Weights control relevance scoring — a match in the `title` field scores 10x higher than a match in `body`.

A collection can have **at most one text index**, but it can cover multiple fields.

## Querying with $text

```javascript
// Simple keyword search
db.articles.find({ $text: { $search: "mongodb aggregation" } });

// Phrase search (wrap in quotes)
db.articles.find({ $text: { $search: "\"compound index\"" } });

// Exclude a word with -
db.articles.find({ $text: { $search: "mongodb -sharding" } });

// Language override
db.articles.find({ $text: { $search: "base de datos", $language: "es" } });
```

Multiple words in `$search` are treated as OR by default. Use `"..."` for exact phrase, `-word` to exclude.

## Sorting by Relevance Score

MongoDB computes a text score for each matched document. Project and sort on it:

```javascript
db.articles.find(
  { $text: { $search: "replica set failover" } },
  { score: { $meta: "textScore" } }
).sort({ score: { $meta: "textScore" } });
```

`$meta: "textScore"` both projects the computed field and tells the sort stage to use it.

## Text Search vs Atlas Search

| Feature | Built-in Text Index | Atlas Search (Lucene) |
|---|---|---|
| Setup | One `createIndex` call | Atlas cluster only, Atlas UI |
| Stemming | Basic | Full per-language |
| Fuzzy matching | No | Yes (`fuzzy` option) |
| Faceted search | No | Yes |
| Autocomplete | No | Yes |
| Highlighting | No | Yes |
| Infrastructure | Self-hosted or Atlas | Atlas only |

For simple keyword lookups the built-in text index is sufficient. For production search features (autocomplete, facets, typo tolerance), Atlas Search is the right tool.

## Limitations

- Only one text index per collection.
- Cannot combine `$text` with other index types in the same query (except equality on other fields that can use a filter before the text scan).
- Case-insensitive and diacritic-insensitive by default; diacritic sensitivity can be controlled with the `textIndexVersion`.
- Text indexes consume significant RAM and disk — only add one if you need full-text search.

## Quick Example: Product Catalog Search

```javascript
// Setup
db.products.createIndex(
  { name: "text", description: "text" },
  { weights: { name: 3, description: 1 } }
);

// Find products matching "wireless keyboard"
db.products.find(
  { $text: { $search: "wireless keyboard" }, inStock: true },
  { score: { $meta: "textScore" }, name: 1, price: 1 }
).sort({ score: { $meta: "textScore" } }).limit(10);
```

The `inStock: true` filter narrows results before scoring, because a regular index on `inStock` can be used alongside `$text`.
