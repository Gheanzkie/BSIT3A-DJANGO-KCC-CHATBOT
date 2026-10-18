# KCC Chatbot Assistant

An AI-powered knowledge companion chatbot for Kabankalan Catholic College (KCC) built with Django and MySQL/MariaDB. Ships with a Tabler-based dark UI, email-based authentication, user management with AJAX CRUD, and the **KNIGHT** chat engine (Groq primary with Google Gemini fallback) grounded on a file-based KCC knowledge base.

## Developers

- **Ghean De La Cruz**
- **John Marie Alarcon**

## Admin Login

| Field    | Value            |
|----------|------------------|
| Email    | `admin@admin.com` |
| Username | `admin`           |
| Password | *(set during setup)* |

## Tech Stack

- **Framework:** Django 5.0.14
- **Database:** MySQL / MariaDB (developed against XAMPP MariaDB 10.4.32)
- **AI engines:** KNIGHT v1.0 (Groq) primary, KNIGHT v1.2 (Google Gemini) fallback, Gemini embeddings
- **UI:** Bootstrap 5 / Tabler CSS, Font Awesome 6
- **Python:** 3.13+ (dev-tested on 3.14)

## Project Structure

```
kcc_chatbot_assistant/
├── apps/
│   ├── chat/                    # KNIGHT chatbot app
│   │   ├── knowledge/           # File-based knowledge base (.txt training files)
│   │   ├── management/          # Django management commands
│   │   ├── services/ai.py       # KNIGHT engine chain (Groq → Gemini), KB retrieval, usage stats
│   │   ├── tests/               # Chat app tests
│   │   ├── models.py            # Conversation, Message
│   │   └── urls.py / views.py   # Chat page, send, session CRUD
│   ├── core/                    # Welcome, login, logout, register, dashboard
│   └── users/                   # User model, profile edit, user management CRUD (AJAX)
├── db/
│   └── kcc_chatbot.sql          # Schema-only database dump
├── mysite/                      # Project settings, URLs, WSGI
├── static/                      # Tabler CSS/JS, vendor libs, KCC logo & background
├── templates/                   # HTML templates (welcome, auth, chat, users, theme)
├── kcc_chatbot.sql              # Full database dump (schema + data) from XAMPP
├── pytest.ini                   # Test runner config
└── requirements.txt
```

## Database Dumps

Two SQL dumps are included, both exported from the XAMPP MariaDB server with `mysqldump --databases` (so each already contains `CREATE DATABASE` / `USE` statements):

| File                 | Contents                  |
|----------------------|---------------------------|
| `db/kcc_chatbot.sql` | Schema only (CREATE TABLE)|
| `kcc_chatbot.sql`    | Full dump (schema + data) |

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

### 4. Set up the database

Start MySQL/MariaDB (e.g. XAMPP control panel) and import one of the dumps:

```bash
mysql -u root -p < db/kcc_chatbot.sql      # schema only
mysql -u root -p < kcc_chatbot.sql         # schema + data
```

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
```

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

- **KNIGHT AI Chat** — Answers grounded on the file-based knowledge base; Groq primary engine with automatic Gemini fallback, per-engine reasoning-effort overrides, and an escalation retry when hidden reasoning exhausts the output budget
- **Trainable Knowledge Base** — Drop `.txt` files in `apps/chat/knowledge/` (first line = title, remaining lines = content); auto-reloaded with no restart. Staff can also add facts straight from chat with `remember: <info>` / `tandaan: <info>`
- **Conversations** — Per-user chat threads with engine preference (auto / KNIGHT v1.0 / KNIGHT v1.2) and language (auto / Tagalog / English)
- **Usage Stats** — Per-engine and per-user usage tracking (`usage_stats.json`, `usage_by_user.json` in the chat app)
- **Welcome Page** — Professional dark-themed landing page with KCC branding
- **Authentication** — Email-based login, registration with validation
- **Dashboard** — Admin overview with user stats
- **User Management** — Superadmin can add, edit, deactivate and delete users via AJAX
- **Profile Editor** — Sidebar popup for editing profile and changing password
- **Rate Limiting** — Chat send throttling via `CHAT_MAX_PER_MINUTE` (default 20/min)
- **Responsive UI** — Mobile-friendly Tabler dark theme throughout

## Routes

| URL                   | Description                       |
|-----------------------|-----------------------------------|
| `/`                   | Welcome / landing page            |
| `/login/`             | Login page                        |
| `/register/`          | Registration page                 |
| `/logout/`            | Logout                            |
| `/home/`              | Dashboard (requires login)        |
| `/chat/`              | Chat page (latest conversation)   |
| `/chat/new/`          | Start a new conversation          |
| `/chat/send/`         | Send a message (AJAX)             |
| `/chat/<id>/`         | Open a conversation               |
| `/chat/<id>/delete/`  | Delete a conversation             |
| `/users/`             | User management (superadmin)      |
| `/users/profile/`     | Profile / password edit           |
| `/users/ajax/*`       | User CRUD endpoints (AJAX)        |
| `/admin/`             | Django admin panel                |

## Testing

```bash
pytest
```

Config lives in `pytest.ini` (`DJANGO_SETTINGS_MODULE = mysite.settings`); chat tests in `apps/chat/tests/`.

## Docs

- [SESSION_LOG.md](SESSION_LOG.md) — Full development session log including security audit findings and bug fixes
- `AUDIT_REPORT.md` — Security audit report
- `apps/chat/knowledge/_README.txt` — How to train KNIGHT
