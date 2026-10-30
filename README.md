# KCC Chatbot Assistant

An AI-powered knowledge companion chatbot for Kabankalan Catholic College (KCC) built with Django and MySQL/MariaDB. Ships with a Tabler-based dark/light UI, email-based authentication, a **KNIGHT** chat engine (Groq primary with Google Gemini fallback) grounded on a file-based KCC knowledge base, plus admin modules for announcements, support tickets and activity auditing.

## Developers

- **Ghean De La Cruz**
- **John Marie Alarcon**

## Tech Stack

- **Framework:** Django 5.0.14
- **Database:** MySQL / MariaDB (developed against XAMPP MariaDB 10.4.32), with a bundled SQLite copy for quick local runs
- **AI engine:** one **KNIGHT**, two providers behind it — Groq (`openai/gpt-oss-20b`) answers first, Google Gemini (`gemini-3.8-flash`) takes over automatically when Groq is down or rate-limited. Gemini embeddings power semantic KB search.
- **UI:** Bootstrap 5 / Tabler CSS, Font Awesome 6 — dark theme by default, light theme toggle in the sidebar
- **Python:** 3.13+ (dev-tested on 3.14)

## Admin Login

| Field    | Value                     |
|----------|---------------------------|
| Email    | *(your superuser email)*  |
| Username | `admin`                   |
| Password | *(set during setup)*      |

Login is email-based. Create the account with `python manage.py createsuperuser` — it lands on `/home/` (the admin dashboard). Regular accounts are redirected into the chat instead.

## Project Structure

```
kcc_chatbot_assistant/
├── apps/
│   ├── chat/                      # KNIGHT chatbot app
│   │   ├── knowledge/             # File-based knowledge base (.txt training files)
│   │   ├── management/            # Django management commands
│   │   ├── services/ai.py         # KNIGHT engine chain (Groq → Gemini), KB retrieval, usage stats
│   │   ├── tests/                 # Chat + AI tests (65 tests total project-wide)
│   │   ├── models.py              # Conversation, Message
│   │   └── urls.py / views.py     # Chat page, send, session open/delete, leave beacon
│   ├── core/                      # Landing, auth, dashboard, announcements, tickets, activity log
│   │   ├── models.py              # Announcement, AnnouncementImage, Ticket, ActivityLog
│   │   ├── context_processors.py  # Sidebar sessions, open-ticket badge, announcement counts
│   │   └── urls.py / views.py     # All non-chat routes (see Routes below)
│   └── users/                     # Profile edit + password change (POST only)
├── db/
│   └── kcc_chatbot.sql            # Schema-only database dump
├── mysite/                        # Settings, root URLconf, WSGI/ASGI
├── static/                        # Tabler CSS/JS, vendor libs, KCC logo & background
├── templates/
│   ├── announcements/             # list.html (admin maker), edit.html, history.html (public)
│   ├── activity/list.html         # Admin activity log
│   ├── reports/list.html          # Admin ticket queue
│   ├── chat/, auth/, users/
│   ├── partials/modals.html       # Login, register, profile, report modals
│   └── theme/                     # base.html, sidebar.html, footer.html, messages.html
├── db.sqlite3                     # SQLite copy of the database (tracked in the repo)
├── kcc_chatbot.sql                # Full MariaDB dump (schema + data) from XAMPP
├── pytest.ini                     # Optional pytest runner config
└── requirements.txt
```

## Database

### MariaDB dumps

Both dumps were exported from the XAMPP MariaDB server with `mysqldump --databases`, so each already contains `CREATE DATABASE` / `USE` statements:

| File                 | Contents                   |
|----------------------|----------------------------|
| `db/kcc_chatbot.sql` | Schema only (CREATE TABLE) |
| `kcc_chatbot.sql`    | Full dump (schema + data)  |

### Bundled SQLite copy

`db.sqlite3` is committed to the repository, so you can run the project without a MySQL server:

```ini
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
```

The file carries the full application schema plus whatever data was present when it was committed — including `auth_user` rows and chat history. Treat it as **sensitive**: do not reuse the bundled accounts' passwords anywhere else.

### MySQL strict mode

`mysite/settings.py` attaches `charset=utf8mb4` and `SET sql_mode='STRICT_TRANS_TABLES'` whenever the configured engine is MySQL/MariaDB. Without strict mode MySQL silently truncates over-length values instead of raising, which loses announcement titles/messages. SQLite and PostgreSQL are unaffected — the options are only added for MySQL engines.

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Gheanzkie/BSIT3A-DJANGO-KCC-CHATBOT.git
cd BSIT3A-DJANGO-KCC-CHATBOT
```

### 2. Create virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

`mysqlclient` needs the MariaDB/MySQL client headers; on Windows, building against the XAMPP/MariaDB connector usually needs the matching MSVC toolchain. If you only want the SQLite copy, you can skip it and install `Django`, `requests` and `Pillow` alone.

### 4. Set up the database

Either import a MariaDB dump:

```bash
mysql -u root -p < db/kcc_chatbot.sql      # schema only
mysql -u root -p < kcc_chatbot.sql         # schema + data
```

...or point `DB_ENGINE` at the committed `db.sqlite3` (see above) and skip the import.

### 5. Configure environment

`mysite/settings.py` loads a root `.env` file into the environment; non-empty values in `apps/chat/ai_config.env` win over `.env` for AI settings. Both files are git-ignored — create them locally, never commit them.

Root `.env` (database):

```ini
DB_ENGINE=django.db.backends.mysql
DB_NAME=kcc_chatbot
DB_USER=root
DB_PASSWORD=
DB_HOST=127.0.0.1
DB_PORT=3306
```

`apps/chat/ai_config.env` (KNIGHT engines):

```ini
GROQ_API_KEY=your_groq_key
GEMINI_API_KEY=your_gemini_key
AI_CHAT_MODEL_GROQ=openai/gpt-oss-20b
AI_CHAT_MODEL_GEMINI=gemini-3.8-flash
AI_NAME=KNIGHT
AI_REASONING_EFFORT=low
# AI_REASONING_EFFORT_PRIMARY=medium
# AI_REASONING_EFFORT_FALLBACK=low
```

`AI_NAME` is the single brand shown in the chat bubble (default `KNIGHT`). `AI_PRIMARY_NAME` / `AI_FALLBACK_NAME` are diagnostics only — they label the provider rows on the admin dashboard, they are not shown to chat users.

Other optional settings (dev defaults): `DJANGO_DEBUG=True`, `DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,...`. `SECRET_KEY` comes from `DJANGO_SECRET_KEY`, else a git-ignored `.secret_key` file that is auto-generated on first run.

### 6. Run migrations (if not using a data dump)

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 7. Run the server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` for the welcome page.

## Features

### Chat

- **KNIGHT AI Chat** — answers grounded on the file-based knowledge base; Groq primary with automatic Gemini fallback, per-engine reasoning-effort overrides, and an escalation retry when hidden reasoning exhausts the output budget
- **Public chat** — visitors can chat without an account; the conversation is bound to the browser session and purged when the tab closes (a `leave` beacon marks it, a sweep deletes it)
- **Trainable knowledge base** — drop `.txt` files in `apps/chat/knowledge/` (first line = title, remaining lines = content); auto-reloaded with no restart. Staff can also add facts straight from chat with `remember: <info>` / `tandaan: <info>`
- **One KNIGHT** — no model picker in the UI. The chat shows a single `KNIGHT` label; provider selection (Groq → Gemini) is automatic, with a 90-second cooldown on a provider that just failed. Legacy `primary` / `fallback` values in old conversation rows still resolve correctly
- **Reasoning** — `reasoning_effort` is sent to both providers (`AI_REASONING_EFFORT`, or per-provider `AI_REASONING_EFFORT_PRIMARY` / `AI_REASONING_EFFORT_FALLBACK`). If a provider rejects the parameter with HTTP 400, the request is retried once without it instead of failing; if hidden reasoning exhausts the output budget, one bounded retry runs with `AI_REASONING_ESCALATION_TOKENS`
- **Conversations** — per-user threads with language preference (auto / Tagalog / English); the sidebar lists saved chats on every page
- **Usage stats** — per-engine and per-user tracking (`usage_stats.json`, `usage_by_user.json`)
- **Rate limiting** — chat send throttling via `CHAT_MAX_PER_MINUTE` (default 20/min)

### Admin modules

- **Announcement Maker** (`/announcements/`) — publish title + message with multiple uploaded pictures, then publish/hide or delete from the same table. The sidebar nav entry shows a live count of every announcement (active + hidden)
- **Public announcement board** — signed-out visitors get a read-only history of active announcements. Images open in a fullscreen lightbox with click-to-zoom at native resolution, drag-to-pan, arrow-key navigation and a picture counter. The same lightbox is used inside the floating announcements panel
- **KB sync** — publishing or editing an announcement pushes it into the AI knowledge store, so KNIGHT can answer about it; hiding or deleting removes it again
- **Ticket queue** (`/tickets/`) — visitor reports triaged by status (open/resolved) with a badge count in the sidebar; resolved tickets are archived read-only
- **Activity log** (`/activity/`) — searchable audit trail of logins, registrations and requests with user, IP and path
- **Dashboard** (`/home/`) — conversation/message/ticket totals plus AI model and key status (masked)

### Account & UI

- **Authentication** — email-based login, registration with password validation, and rate limiting with lockout on repeated failures
- **Profile editor** — sidebar popup for editing profile details and changing password
- **Floating quick actions** — Help, Report a Problem and Announcements panels that load beside the sidebar item that opened them
- **Theme toggle** — dark by default; light mode persists in `localStorage`
- **Responsive UI** — collapsible sidebar with backdrop and fab button on mobile

## Routes

| URL                          | Method     | Description                                        |
|------------------------------|------------|----------------------------------------------------|
| `/`                          | GET        | Welcome / landing page                             |
| `/login/`                    | GET, POST  | Login page                                         |
| `/register/`                 | POST       | Registration (modal)                               |
| `/logout/`                   | POST       | Logout                                             |
| `/home/`                     | GET        | Admin dashboard (superuser)                        |
| `/help/`                     | GET        | Help page                                          |
| `/report/`                   | POST       | Submit a report/ticket from the visitor panel      |
| `/announcements/`            | GET, POST  | Admin: maker + list. Public: read-only history     |
| `/announcements/<pk>/edit/`  | GET, POST  | Edit an announcement (superuser)                   |
| `/announcements/<pk>/update/`| POST       | Publish/hide or delete (superuser)                 |
| `/tickets/`                  | GET        | Admin ticket queue (superuser)                     |
| `/tickets/<pk>/update/`      | POST       | Resolve, reopen or delete a ticket (superuser)     |
| `/activity/`                 | GET        | Admin activity log with `?q=` search (superuser)   |
| `/chat/`                     | GET        | Chat page                                          |
| `/chat/open/`                | POST       | Open/select a conversation                         |
| `/chat/new/`                 | POST       | Start a new conversation                           |
| `/chat/send/`                | POST       | Send a message (AJAX)                              |
| `/chat/leave/`               | POST       | Leave beacon for public chats                      |
| `/chat/history/`             | POST       | Conversation history (JSON)                        |
| `/chat/<token>/`             | GET        | Open a conversation by token                       |
| `/chat/<token>/delete/`      | POST       | Delete a conversation                              |
| `/users/profile/`            | POST       | Update profile                                     |
| `/users/password/`           | POST       | Change password                                    |
| `/admin/`                    | GET        | Django admin panel                                 |

## Testing

The suite runs on Django's own test runner:

```bash
python manage.py test
```

65 tests currently pass (chat flow, token access control, public-chat lifecycle, AI retry/escalation, source formatting, core redirects, single-KNIGHT naming contract, and the reasoning-parameter fallback). `pytest.ini` is also committed for anyone who installs `pytest-django`:

```bash
pip install pytest pytest-django
pytest
```

## Docs

- [SESSION_LOG.md](SESSION_LOG.md) — development session log including security audit findings and bug fixes
- `AUDIT_REPORT.md` — security audit report
- [KCC-CHATBOT-ASSISTANCE.docx](KCC-CHATBOT-ASSISTANCE.docx) — capstone project paper, aligned with the implemented system (AI chat, file-based KB, ticket queue + reply flagging, admin/student access control)
- `apps/chat/knowledge/_README.txt` — how to train KNIGHT

## Repository Notes

- `.env`, `.secret_key`, `apps/chat/ai_config.env`, `media/`, `.venv/`, `__pycache__/` and the AI usage JSON files are git-ignored.
- `db.sqlite3` **is** committed (force-added past `.gitignore`), so anyone cloning gets the database contents including user rows — keep that in mind before making the repository public.
- Uploaded announcement images live under `media/` and are **not** committed; database rows that reference them resolve to nothing on a fresh clone.
