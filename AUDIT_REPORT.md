# KCC Chatbot (KNIGHT) — Phase 1 Audit Report

**Date:** 2026-10-17
**Project:** C:\python\project\kcc_chatbot_assistant
**Method:** Full static inspection of source files + runtime verification (`manage.py check`, `showmigrations`). No files were modified.
**Work order:** kcc_chatbot.txt (12-phase improvement plan)

---

## 0. Verified runtime state (evidence)

| Check | Result |
|---|---|
| `python manage.py check` | `System check identified no issues (0 silenced).` |
| `showmigrations chat` | 0001–0004 all `[X]` (applied) |
| `showmigrations users` | 0001 `[X]` (applied) |
| Database engine (`.env`) | `mysql` / db `kcc_chatbot` @ localhost:3306 |
| AI keys location | `apps/chat/ai_config.env` (gitignored) — GROQ_API_KEY, GEMINI_API_KEY, model overrides present |
| Secrets in git | None — `git ls-files` shows no `.env`, `.secret_key`, or `ai_config.env` |
| Hardcoded API keys in source | 0 matches for `gsk_*` / `AIza*` patterns in `ai.py` |
| Live usage (`usage_stats.json`) | groq: 34 calls / 19,536 tokens; embeddings: 24 calls / 29 items (last call 2026-10-17 19:58) |

Files inspected: `mysite/settings.py`, `mysite/urls.py`, `apps/chat/{models,views,urls,admin,apps}.py`, `apps/chat/services/ai.py` (925 lines), `apps/chat/{replies.txt,knowledge/*,usage_stats.json}`, migrations 0001–0004, `apps/core/{views,urls}.py`, `apps/users/{models,views,forms,urls}.py`, `templates/chat/chat.html`, `pytest.ini`, `requirements.txt`, `README.md`, `SESSION_LOG.md`, `.env` (key names), `apps/chat/ai_config.env` (key names), `.gitignore`.

---

## 1. What currently works

- **Django 5.0.14 + MySQL/MariaDB** — clean system check, all migrations applied. Auth app `users.User` (AbstractUser, email login, `db_table='auth_user'`).
- **Two AI engines with fallback chain** (`ai.py`): Groq (primary, OpenAI-compatible `/chat/completions`) and Gemini (fallback, OpenAI-compat endpoint). `_ENGINE_ORDER` supports `auto` / `primary` / `fallback` preference. Both speak the same `_chat_openai` interface.
- **Config is fully env-driven** — base URLs, model names, keys, timeouts, KB thresholds (`AI_KB_TOP_K=3`, `AI_KB_MIN_SCORE=0.6`), history depth (`AI_MAX_HISTORY=6`) all from settings; `ai_config.env` overrides `.env` for AI keys.
- **File-based knowledge base** (`apps/chat/knowledge/*.txt`): first line = title, subfolders = categories, auto-loaded, no DB. Currently 3 notes (car pass, access directions, CMAT dean's office).
- **Semantic retrieval**: Gemini `batchEmbedContents` (3072-dim vectors), JSON vector cache (`_embeddings.json`) keyed by SHA-256 fingerprint of all KB content + embed model → auto-refreshes on any change. Cosine similarity, top-k, min-score gate.
- **Keyword fallback retrieval** when embeddings unavailable — pipeline never hard-fails on retrieval.
- **Full RAG pipeline** (`answer_question`): smalltalk/canned replies → KB retrieval → DuckDuckGo web search → prompt selection (KB-only / web-only / KB+web combined) → chat call → reply + engine + sources dict.
- **Canned reply system**: `replies.txt` (greeting/train/who/capabilities/thanks/bye × tl/en/mix) with mtime auto-reload; built-in fallbacks in code.
- **Chat-driven knowledge adds**: staff `remember:` / `tandaan:` prefix writes a note file; auto-learn extracts KCC facts from messages via LLM JSON extraction.
- **Conversation persistence**: `Conversation` + `Message` models, user-scoped queries enforced (`filter(user=request.user)`, `get_object_or_404(..., user=...)`), last-6-message history passed to the model, language auto-detection on first message, per-session delete, Django admin registered for both models.
- **Usage telemetry**: per-engine call/token counters + Groq rate-limit headers in `usage_stats.json`; dashboard (`/home/`) renders masked keys, model, endpoint, and usage per slot.
- **Web UI**: Gemini-style chat layout, fetch-based send with CSRF token, `textContent`-safe rendering (no stored XSS), New Chat / session list / delete.
- **Security baseline**: login + register rate limiting via Django cache (per-IP + per-account), password validators, generic registration errors (anti-enumeration), CSRF on all POSTs, superuser-gated user CRUD, profile edit with session-hash update, no secrets in frontend/git, message size cap 2000 chars.

## 2. What is incomplete or unreliable (vs the 12-phase plan)

| # | Gap | Evidence | Phase |
|---|---|---|---|
| G1 | **Citations computed but never shown.** `answer_question()` returns `sources`; `views.py` drops it (`reply, engine = result['reply'], result['engine']`); `JsonResponse` has no `sources`; `chat.html` renders none. Message model has no sources field. | views.py:155-156, 178-184; chat.html | P3 |
| G2 | **Web search runs on EVERY question ≥10 chars** — even with a strong KB match. Plan: "avoid searching the web for every trivial conversation". Adds latency + rate-limit pressure to every answer. | ai.py:882-884 | P3/P8 |
| G3 | **Auto-learn is not staff-gated and not reviewed.** `chat_send` runs `ai.auto_learn(text)` for **every user**; facts are written directly into the KB. Plan P7: "Never automatically treat every user message... as verified truth"; "administrator review". Any account can poison the KB. | views.py:144-147; ai.py:721-757 | P7 |
| G4 | **Web snippets auto-saved as KB facts** without verification — `_save_web_fact(web)` persists top result snippet + URL as a knowledge note. Same trust problem as G3. | ai.py:905, 847-865 | P3/P7 |
| G5 | **No page-content extraction.** Web research uses DuckDuckGo snippets only (HTML scrape, regex-parsed). No full-page fetch, no publication dates, no credibility/freshness checks, no multi-source comparison, no result caching. | ai.py:799-844 | P3 |
| G6 | **No retry/backoff, no latency logging.** A single transient 5xx/timeout fails the provider immediately (`chat()` moves to next slot). Usage log has tokens but no latency. | ai.py:283-286, 353-388 | P2/P11 |
| G7 | **No chat rate limiting.** `/chat/send/` can be hammered by any authenticated user; free-tier quota drain. Login/register are limited, chat isn't. | views.py:85-97 | P9 |
| G8 | **No conversation summarization.** Hard 6-message window; older context is simply dropped in long threads. No "clear all history" control (only per-session delete). | views.py:150-151; ai.py AI_MAX_HISTORY=6 | P6 |
| G9 | **Facebook announcement capability: absent.** No trusted-source config, no admin workflow for approved posts, no Meta API, no discovery/freshness tracking. | no code | P4 |
| G10 | **No feedback loop.** No helpful/unhelpful, no corrections, no admin review queue, no unanswered-question tracking (only log lines). | no models/UI | P7 |
| G11 | **No RAG metadata.** No per-item dates, verification status, content hash, or deactivation workflow. Chunking: whole file = 1 item, prompt-capped at 1200 chars — long documents will be truncated. | ai.py:40, 548-603, 642-647 | P5 |
| G12 | **Dashboard stubs.** `total_conversations` / `total_messages` render `'—'` — models exist, counts trivial to wire. | core/views.py:166-167 | P10 |
| G13 | **No tests for chat.** `pytest.ini` configured; only `apps/core/tests.py` (668 B) and `apps/users/tests.py` (63 B) exist. No provider mocks, no eval dataset, no citation tests. | file listing | P12 |
| G14 | **Gemini fallback never exercised** (no `gemini` row in usage_stats — only `groq` + `embeddings`). Untested safety net in practice. | usage_stats.json | P2/P12 |

## 3. What is duplicated or unnecessarily complex

- `KnowledgeItem` / `KnowledgeCategory` models were **intentionally removed** (migration 0003) — file-based KB replaced them. No duplication: dead schema is gone. `db.sqlite3` (192 KB) in the root is unused when `.env` selects MySQL (gitignored; safe leftover).
- `_SMALLTALK` built-in dict duplicates `replies.txt` sections — by design (file wins, dict = fallback). Acceptable; keep.
- `views.py chat_send` is mildly fat: validation + engine pref + language detection + teach prefix + auto-learn + history assembly + error mapping in one view. Plan P8 wants service modules with clear responsibilities → extract `services/chat_flow.py` gradually.
- Two env files (`.env`, `ai_config.env`) with override precedence — documented in settings; fine for a student project, just keep the README accurate.

## 4. What should be retained (do NOT touch)

1. `services/ai.py` architecture — provider abstraction, engine order, file-KB design, embeddings cache fingerprinting, keyword fallback, canned replies file.
2. All existing models + migrations (safe history; no resets — rules #11/#296).
3. `_ENGINE_ORDER` fallback logic and error taxonomy (`AIConfigError` / `AIUnavailable`).
4. `usage_stats.json` telemetry approach.
5. Current security posture: rate-limited auth, CSRF, user-scoped conversation access, XSS-safe rendering, secrets hygiene (gitignore verified).
6. File-based KB workflow (admin-friendly, no DB) — extend with metadata instead of replacing.

## 5. What should be changed (prioritized)

**P0 — safe quick wins (no DB migration, no destructive edits):**
1. Persist + render citations: include `sources` in the `chat_send` JSON response; render as clickable links under assistant replies in `chat.html` (textContent-safe). Files: `apps/chat/views.py`, `templates/chat/chat.html`.
2. Gate auto-learn: restrict `ai.auto_learn()` to staff accounts only (default), keeping the explicit `remember:`/`tandaan:` path. File: `apps/chat/views.py`.
3. Conditional web research: add `needs_research(question, items)` — skip web when KB score is strong and question has no freshness/event hints (latest, update, kailan, bagong, announcement, schedule...). File: `apps/chat/services/ai.py`.
4. Retry + backoff (2 retries, jittered) and latency logging for provider calls; log latency into `usage_stats.json`. File: `apps/chat/services/ai.py`.
5. Chat rate limiting (cache-based, mirroring the login limiter) in `chat_send`. Files: `apps/chat/views.py`, `mysite/settings.py`.
6. Disable unverified web-fact auto-save (`_save_web_fact`) or move it behind an explicit `AI_WEB_SAVE_FACTS` env flag defaulting to False. File: `apps/chat/services/ai.py`.

**P1 — DB migrations (needs operator approval before applying):**
7. `Message.sources` (JSONField) to persist citations; feedback models (`MessageFeedback`, `UnansweredQuestion`), admin review queue.
8. Conversation summarization: store rolling summary on `Conversation`, extend context beyond the 6-message window.
9. `TrustedSource` model (official FB pages, website, docs) + admin config — foundation for Phase 4.

**P2 — features:**
10. Facebook announcement research (trusted-source discovery via existing web search + admin manual-add workflow; no login-wall bypass).
11. Wire real dashboard counts (conversations/messages) from existing models.
12. Chat test suite: pytest + `requests` mocks for providers, retrieval, citations, rate limits; small golden Q&A evaluation set.

## 6. Exact files to modify / create (Phase 1 = P0)

| Action | File |
|---|---|
| Modify | `apps/chat/services/ai.py` — `needs_research()`, retry/backoff, latency logging, web-save flag |
| Modify | `apps/chat/views.py` — sources in response, staff-gated auto-learn, chat rate limit |
| Modify | `templates/chat/chat.html` — render source links |
| Modify | `mysite/settings.py` — new env knobs (`CHAT_MAX_PER_MINUTE`, `AI_WEB_SAVE_FACTS`, retry counts) |
| Create | `apps/chat/tests/__init__.py`, `apps/chat/tests/test_ai.py`, `apps/chat/tests/test_chat_views.py` |

## 7. Risks to existing features and data

- **No destructive operations proposed.** No DB resets, no table drops, no data deletion (rules #11/#296). P0 touches only Python/template logic.
- Auto-learn gating (P0-2) changes behavior: non-staff messages will no longer add KB entries — intended by plan P7 but changes current "learning" feel; existing 3 notes unaffected.
- Conditional web research (P0-3) may reduce answer breadth for ambiguous questions — mitigate with conservative hint list; KB+web combine path stays for research-triggering questions.
- Retry (P0-4) adds bounded latency (max 2 retries × backoff) on provider failures — cap total to keep chat responsive.
- Rate limit (P0-5) could lock out power users during testing — set generous defaults (e.g., 20/min) and env-tunable.
- Neither Gemini nor Groq model names are validated against live provider catalogs — fallback path is untested in practice (G14); include a provider smoke test in P2.

## 8. Phased implementation plan with tests

| Step | Change | Test |
|---|---|---|
| P0.1 | Citations end-to-end | Manual: ask a KCC question → links appear; unit: `answer_question` sources passed through view |
| P0.2 | Staff-gated auto-learn | Unit: non-staff POST leaves KB unchanged; staff `tandaan:` writes note |
| P0.3 | Conditional research | Unit: KB-strong question → no web call (mock asserts); "latest announcement" → web called |
| P0.4 | Retry/backoff + latency | Unit: first call 503 → second succeeds; latency key present in usage record |
| P0.5 | Chat rate limit | Unit: N+1 rapid POSTs → 429-style JSON error |
| P0.6 | Web-save flag off | Unit: web answer does not create note file when flag off |
| P0.x | Regression | `python manage.py check` + full pytest run + smoke chat in browser |
| P1 | Migrations (sources field, feedback, trusted sources, summary) | `makemigrations` review + `migrate` on dev DB + model tests |
| P2 | Facebook research, dashboard counts, eval suite | Golden Q&A set: retrieval relevance, citation accuracy, context retention |

**Definition of done per P0 item:** change + test written + `pytest` green + manual chat smoke + no new errors in server log.

---

*Audit rule honored: nothing in this report claims a file, table, or feature exists without inspection evidence; runtime claims are backed by command output in the session.*
