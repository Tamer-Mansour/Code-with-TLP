# TLP Chat — AI Assistant & Semantic Search — Implementation Plan

**App:** Code with TLP · **Feature:** "TLP Chat" · **Drafted:** 2026-05-27

An in-app AI assistant that **knows everything in the system** about the learner — their
courses, lessons, solved challenges, and progress — powered by **vector search + RAG**, with
**bring-your-own API keys** for any model (OpenAI/GPT, Gemini, Claude, DeepSeek, and Chinese
models), and the latest AI features (thinking, reasoning, tool use, web search, streaming).

Built in two layers, in this order:

1. **Layer A — Semantic Search (build first).** Vector + keyword search across everything the
   user can access (courses, lessons, exercises) and everything they own (submissions, progress,
   enrollments). Includes "enroll from search results."
2. **Layer B — TLP Chat.** A RAG assistant on top of that search that answers questions, explains
   the user's progress, and reviews the challenges they've solved.

---

## 1. Stack context

- **Backend:** FastAPI 0.115 · SQLAlchemy 2.0 · SQLite · JWT auth (student + admin).
- **Domain models already present:** `User`, `Subject`, `Course`, `Module`, `Lesson`,
  `Exercise`, `TestCase`, `Submission`, `Enrollment`, `LessonProgress`, `Tag`, `LearningPath`.
- **Frontend:** Angular 21 standalone · Tailwind · ngx-markdown · Monaco · lucide.

Design principle: **stay zero-infra on SQLite** for the MVP, with a clean seam to swap the
vector store later if it grows.

---

## 2. High-level architecture

```
                ┌──────────────────────────── Frontend (Angular) ───────────────────────────┐
                │  Global Search bar     TLP Chat page     Progress-insights widget          │
                └───────────────┬───────────────┬───────────────────────┬────────────────────┘
                                │ /search        │ /chat (SSE stream)    │ /chat/insights
                ┌───────────────▼───────────────▼───────────────────────▼────────────────────┐
                │                         FastAPI  (api/v1)                                    │
                │  SearchService     RAG Orchestrator     ProviderGateway     KeyVault          │
                │       │                  │  (tools)            │  (BYO keys)    (encrypted)    │
                │  ┌────▼─────┐     ┌───────▼────────┐    ┌───────▼─────────────────────────┐   │
                │  │ Embedder │     │ Retriever       │    │ OpenAI / Anthropic / Gemini /   │   │
                │  │ (local)  │     │ (hybrid search) │    │ DeepSeek / Qwen / GLM / Kimi... │   │
                │  └────┬─────┘     └───────┬────────┘    └─────────────────────────────────┘   │
                │  ┌────▼──────────────────▼─────┐                                              │
                │  │  Vector store (sqlite-vec)   │  +  BM25/FTS5 keyword index                 │
                │  │  chunks: content + user data │                                             │
                │  └──────────────────────────────┘                                            │
                └──────────────────────────────────────────────────────────────────────────────┘
```

---

# LAYER A — Semantic Search (build first)

## 3. What gets indexed

| Source | Scope | Chunk content | Metadata |
|---|---|---|---|
| Lessons (`content_md`) | global (published) | per-section chunks | course_id, module_id, lesson_id, type |
| Exercises (`prompt_md`) | global (published) | prompt + tags | exercise_id, difficulty, course_id |
| Courses / Modules | global | title + summary/description | course_id, subject |
| **User submissions** | per-user | code + status + language | user_id, exercise_id, status |
| **Lesson progress** | per-user | completed/in-progress facts | user_id, lesson_id |
| **Enrollments** | per-user | enrolled courses + progress % | user_id, course_id |

Two namespaces: **global content** (shared) and **user data** (private, filtered by `user_id`).

## 4. Vector store & embeddings

- **Vector store:** **`sqlite-vec`** — a vector virtual table inside the existing SQLite DB. No new
  infrastructure, transactional with the app data. (Seam kept clean to swap for **Qdrant** or
  **pgvector** if scale demands.)
- **Keyword index:** SQLite **FTS5** (BM25) for hybrid search.
- **Embeddings:** a **single server-managed embedding model** so all vectors share dimensions —
  e.g. local `bge-small-en-v1.5` / `e5-small` (free, offline) or a configurable provider embedding
  (OpenAI `text-embedding-3-small`, Gemini embeddings). **Do not** use per-user chat keys for
  embeddings (dimension mismatch). This is an explicit, important decision.

## 5. Ingestion pipeline

1. **Chunk** content (markdown-aware, ~300–500 tokens, overlap) → normalize.
2. **Embed** each chunk with the server embedder.
3. **Upsert** into `sqlite-vec` + FTS5 with metadata.
4. **Keep fresh:** re-index on content change (admin lesson/exercise edits already go through known
   endpoints — hook ingestion there) and on user events (new submission, lesson completed).
   Batch reindex command for full rebuilds (mirrors the seed/import pattern).

## 6. Hybrid search

- Run **vector** (semantic) + **BM25** (keyword) in parallel, merge with **Reciprocal Rank
  Fusion**, optionally **re-rank** top-K with a cross-encoder later.
- **Always filter by access:** global content + only the requesting user's private rows.

## 7. Search API & UX

- `POST /api/v1/search` → `{ query, filters }` → ranked, typed results (lesson / exercise / course /
  submission / progress) with snippets + deep links.
- **Frontend:** a global search bar (⌘K palette) returning grouped results; each course result has an
  **Enroll** action (calls existing `POST /progress/enroll/{course_id}`) — satisfies "search into
  everything and enroll into the account."

---

# LAYER B — TLP Chat (RAG assistant)

## 8. RAG flow

1. User message + recent history → **rewrite/expand** query.
2. **Retrieve** from hybrid search, **scoped to this user** (their progress, submissions, plus
   global content).
3. Build a **grounded prompt** (system persona "TLP Chat" + retrieved chunks + the user's profile
   summary) and call the **user's chosen model** via the ProviderGateway.
4. **Stream** the answer with **inline citations** back to the source lessons/exercises.

## 9. Agentic tools (user-scoped function calling)

TLP Chat can call typed tools instead of guessing:

| Tool | Returns |
|---|---|
| `semantic_search(query)` | top chunks across content + user data |
| `get_my_progress()` | enrollments, % complete, streak, lessons done |
| `list_solved_challenges(filter)` | exercises the user passed (status=accepted) |
| `get_course_tree(slug)` | modules/lessons of a course |
| `recommend_next()` | next lesson/exercise from progress gaps |
| `enroll(course_id)` | enroll the user in a course |
| `get_submission(id)` | a past submission's code + result |

## 10. "Understand my progress" feature

A first-class action ("How am I doing?") that runs RAG over the user's data and produces a
structured report: completed vs remaining, strengths/weaknesses by topic, solved-challenge summary
(by difficulty/language), and a recommended next step — all **cited** to real lessons/exercises.
Also surfaced as a **dashboard widget**.

---

## 11. Bring-your-own keys & multi-provider

### 11.1 Provider gateway
A unified `ProviderGateway` normalizes chat across providers (streaming, tools, thinking). Most
Chinese providers expose **OpenAI-compatible** endpoints, so one OpenAI-style adapter + native
adapters for Gemini/Anthropic covers nearly everything. Recommended: **LiteLLM** as the
normalization layer (100+ providers, streaming, tool-calling) — or a thin in-house adapter set
(consistent with the existing Mezan gateway pattern).

### 11.2 Supported providers

| Provider | Example models | API style | Thinking/Reasoning | Tools | Vision |
|---|---|---|---|---|---|
| **OpenAI** | GPT-4.1, GPT-4o, o-series (reasoning) | native / OpenAI | ✅ (o-series) | ✅ | ✅ |
| **Anthropic** | Claude Opus/Sonnet/Haiku 4.x | native | ✅ extended thinking | ✅ | ✅ |
| **Google Gemini** | Gemini 2.5 Pro/Flash | native | ✅ thinking | ✅ | ✅ + search grounding |
| **DeepSeek** | DeepSeek-V3 (chat), R1 (reasoner) | OpenAI-compatible | ✅ (R1) | ✅ | – |
| **Alibaba Qwen** | Qwen3, QwQ, Qwen-VL | OpenAI-compatible (DashScope) | ✅ (QwQ/Qwen3) | ✅ | ✅ (VL) |
| **Moonshot / Kimi** | Kimi K2 (long context) | OpenAI-compatible | partial | ✅ | – |
| **Zhipu / GLM** | GLM-4.6 | OpenAI-compatible | ✅ | ✅ | ✅ (GLM-V) |
| **Baidu ERNIE** | ERNIE 4.x | native/compatible | partial | ✅ | ✅ |
| **MiniMax / 01.AI (Yi)** | abab, Yi-Large | OpenAI-compatible | – | ✅ | partial |
| **xAI Grok / Mistral** | Grok, Mistral Large | OpenAI-compatible | partial | ✅ | partial |
| **Local / self-hosted** | vLLM / Ollama (OpenAI-compatible) | OpenAI-compatible | model-dependent | ✅ | model-dependent |

(Capabilities are detected per model from a **model registry** so the UI only shows what a model
supports.)

### 11.3 Key storage & selection
- Users add keys in **Settings → AI Keys**: provider, API key, optional base URL, default model.
- Keys **encrypted at rest** (Fernet/AES with a server-held key), **never returned to the client**,
  **never logged**, used only server-side.
- Per-user **model picker** in chat; remembers last used; per-provider connection test.

---

## 12. Latest AI features to support

- **Thinking / reasoning** — request reasoning effort where supported; render the reasoning trace in
  a collapsible "Thinking" accordion (o-series, DeepSeek-R1, Gemini thinking, Claude extended
  thinking, QwQ/Qwen3).
- **Tool / function calling** — the agentic tools in §9.
- **Web search** — provider-native grounding (Gemini) or a search tool fallback.
- **Streaming** — token streaming over SSE/WebSocket.
- **RAG citations** — clickable sources under each answer.
- **Vision** — attach diagrams/screenshots (for capable models).
- **Prompt caching** — cache the system prompt + retrieved context for providers that support it
  (cost/latency win).
- **Structured outputs** — JSON mode for the progress report and recommendations.

---

## 13. New backend data model

| Table | Key fields |
|---|---|
| `user_ai_key` | user_id, provider, encrypted_key, base_url, default_model, enabled |
| `chat_session` | id, user_id, title, model, created_at |
| `chat_message` | id, session_id, role, content, model, tokens_in/out, thinking, citations(JSON) |
| `embedding_chunk` | id, source_type, source_id, user_id (nullable=global), text, metadata(JSON) |
| `vec_chunks` | `sqlite-vec` virtual table: chunk_id ↔ embedding |
| `chunks_fts` | FTS5 mirror of chunk text for BM25 |

## 14. API surface (api/v1)

```
POST /search                      hybrid search (typed results + enroll links)
GET  /ai/providers                supported providers + model registry
GET/POST/DELETE /ai/keys          manage BYO keys (write-only secrets)
POST /ai/keys/{id}/test           connection test
GET  /chat/sessions               list / create / rename / delete
POST /chat/sessions/{id}/messages send message → SSE stream (tokens, thinking, tool calls, citations)
POST /chat/insights               "understand my progress" structured report
POST /admin/search/reindex        full reindex (admin)
```

---

## 15. Frontend UX (modern & productive)

- **TLP Chat page**: streaming markdown + Monaco code blocks, collapsible **Thinking** panel,
  **citations** chips, model picker (with capability badges), conversation sidebar, suggested
  prompts, and **context buttons** ("Ask about this lesson/exercise" from lesson/exercise pages).
- **Global ⌘K search** palette: grouped, typed results with enroll/open actions.
- **Progress-insights widget** on the dashboard.
- **Settings → AI Keys** screen with per-provider cards + test button.
- Matches the app theme (purple→blue gradient, dark/light), responsive, optimistic streaming.

---

## 16. Security & privacy

- BYO keys encrypted, server-side only, never logged/echoed.
- **Strict user-scoped retrieval** — a user can never retrieve another user's private chunks.
- Rate limiting + per-request token budgets; redact secrets from prompts.
- Clear data-use notice: messages go to the **user's own** provider with their key.

---

## 17. Phased roadmap

| Phase | Deliverable |
|---|---|
| **0 — Providers + basic chat** | KeyVault, ProviderGateway (OpenAI-compatible + Gemini + Anthropic), Settings → AI Keys, plain streaming chat (no RAG yet). |
| **1 — Semantic search (Layer A)** | sqlite-vec + FTS5, ingestion of content + user data, `POST /search`, ⌘K search UI with enroll. |
| **2 — RAG chat (Layer B)** | retrieval + grounded prompts + citations + conversation persistence. |
| **3 — Agentic + reasoning** | tools (§9), thinking/reasoning rendering, web search, model capability registry. |
| **4 — Insights & polish** | "Understand my progress" report + dashboard widget, vision, prompt caching, structured outputs, re-ranking. |

---

## 18. Recommended decisions

- **Vector store:** `sqlite-vec` (zero-infra, fits SQLite); abstract behind a `VectorStore`
  interface to allow Qdrant/pgvector later.
- **Embeddings:** one **server-managed** model (local `bge-small`/`e5` or a default provider) — never
  per-user, to keep dimensions consistent.
- **Provider normalization:** **LiteLLM** (fastest path to all providers incl. Chinese ones) unless
  you prefer reusing the in-house gateway pattern.
- **Build order:** Phase 0 → 1 (search) → 2 (RAG) — exactly the "search before AI" you asked for.

---

## 19. Open questions

- Embeddings: local model (free, offline, needs CPU/RAM) vs a default cloud embedding key (simpler,
  costs money, needs one server key)?
- Should the server ship a **default/free model** so users without a key can still try TLP Chat, or
  is BYO-key **required**?
- Provider layer: **LiteLLM** dependency vs in-house adapters (reuse Mezan gateway)?
- Privacy stance for user code/submissions being sent to third-party providers — opt-in per user?
