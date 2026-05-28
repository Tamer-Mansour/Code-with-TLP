# Interview Q&A seed format

One JSON file per category at `backend/seed/interview/<slug>.json`. The loader
(`backend/seed/import_interview.py`) reads every `*.json` here into the
`interview_categories` + `interview_questions` tables.

## Schema

```json
{
  "category": {
    "name": "System Design",
    "slug": "system-design",
    "description": "Designing scalable, reliable distributed systems.",
    "icon": "server",
    "color": "#ef4444",
    "order_index": 3
  },
  "questions": [
    {
      "question": "Design a URL shortener like bit.ly.",
      "answer": "## Clarify requirements\n- ~100M URLs/day ...\n\n## High-level design\n1. ...\n\n```\nclient -> LB -> app -> cache -> DB\n```\n\n**Key points:** base62 encoding, ...",
      "difficulty": "hard",
      "tags": ["scalability", "hashing", "caching"]
    }
  ]
}
```

## Rules
- `slug`: lowercase-kebab, unique across files.
- `icon`: a lucide icon name (e.g. `cpu`, `server`, `database`, `network`, `code`, `brain`, `git-branch`, `lock`, `layers`).
- `color`: hex string.
- `answer`: **Markdown** — use headings, bullet/numbered lists, fenced code blocks, tables, and **bold** for key terms. Make answers genuinely useful for learning (a few short paragraphs each), not one-liners.
- `difficulty`: `easy` | `medium` | `hard`.
- `tags`: array of short lowercase strings.
- Aim for **15–22 questions per category**, ordered roughly easy → hard.
- Valid JSON only (escape newlines as `\n`, quotes as `\"`).
