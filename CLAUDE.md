# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

SUZURAN is a Flask + SQLite web app for managing university student (mahasiswa) records — an academic project ("Tugas Akhir") demonstrating CRUD, search, and sorting algorithms. Code comments, UI text, route documentation, and flash messages are in **Indonesian**; match that language when editing user-facing strings.

## Commands

```bash
pip install -r requirements.txt   # install deps (Flask, gunicorn)
python app.py                     # run locally → http://localhost:5000 (debug=False)
gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 60   # production (Render)
```

- Default login: username `admin`, password `admin123` (auto-seeded on first run if `users` table is empty).
- No test suite, linter, or build step exists.
- The SQLite DB (`suzuran.db`) and its tables are created automatically on startup via `db.init_tables()` + `db.seed_admin()` — deleting the file resets all data.

### Environment variables

| Var | Purpose |
|-----|---------|
| `PORT` | server port (default 5000) |
| `SECRET_KEY` | Flask session secret (defaults to a hardcoded value) |
| `GMAIL_USER` | Gmail address used to send student emails |
| `GMAIL_APP_PASSWORD` | Gmail **App Password** (16 digits, not the normal account password) |
| `GMAIL_SENDER_NAME` | display name for outgoing email (optional) |

Deployment config is in `render.yaml`. On Windows/PowerShell set vars with `$env:NAME = "value"` before `python app.py`; an `.env` file is gitignored but **not auto-loaded** (no python-dotenv) — export the vars into the environment yourself.

## Architecture

`app.py` is the single Flask controller holding **all** routes; business logic lives in OOP classes under `utils/`. The flow for any data operation is: route → `Validator` → `Mahasiswa` model → `Database`, with results rendered through Jinja templates in `templates/`.

- **`utils/database.py` (`Database`)** — the only module that touches SQLite. All access goes through the `_connect()` context manager (auto commit/rollback/close, `sqlite3.Row` factory, WAL mode). Owns the schema for three tables: `users`, `mahasiswa`, `search_log`. Passwords are SHA-256 hashed via `_hash()`. Methods that insert/update accept a `Mahasiswa` object and read its properties.

- **`utils/mahasiswa.py` (`Mahasiswa`)** — the data model. Uses `__slots__` + read-only properties. The constructor **normalizes** input (NIM→upper, nama→title case, email→lower, ipk→float). This normalization is why routes build a `Mahasiswa` before persisting rather than passing raw form dicts.

- **`utils/validator.py` (`Validator`)** — regex-based field validation. `validate_mahasiswa()` returns a dict `{field: error_message}` (empty = valid). The compiled regex patterns in `POLA` are the source of truth for accepted formats (NIM 8–12 digits, IPK 0.00–4.00, etc.). Validation runs **before** constructing the model, on raw form data.

- **`utils/algoritma.py` (`SearchEngine`, `SortEngine`)** — deliberately hand-rolled search/sort for the project's educational purpose. These return `(results, step_count)` and expose `estimasi*` methods for theoretical complexity. Do **not** replace them with Python built-ins — counting steps and demonstrating O(n)/O(log n)/O(n²) is the point. `SearchEngine` supports `linear_search` (any field, substring) and `binary_search` (by NIM, requires sorted data). `SortEngine` supports `bubble_sort` and `selection_sort`; `_get_val` coerces to float when possible, else lowercased string.

- **`utils/mailer.py` (`EmailSender`)** — sends email to a student via Gmail SMTP (`smtp.gmail.com:587`, STARTTLS). Reads credentials from the `GMAIL_*` env vars. `is_configured()` gates sending; `send()` returns `(success, message)` and never raises — auth/SMTP failures come back as a message string. Routes and the compose template both check `is_configured()` so the UI degrades gracefully (warning banner + disabled button) when credentials are absent.

### Key conventions

- **Auth**: every route except `/login` is gated by the `@login_required` decorator, which checks `session["user_id"]`.
- **JSON API endpoints** (`/api/cari`, `/api/sort`, `/api/log/*`) accept/return JSON and are called from the search/sorting/log pages via JS; they wrap logic in try/except and return `{"error": ...}` with a 4xx/5xx status on failure.
- **Page routes** use `flash()` + redirect for feedback (toast alerts rendered in `base.html`).
- **NIM uniqueness** is enforced in the route layer via `db.nim_exists(nim, exclude_id=...)`, not only by the DB UNIQUE constraint — pass `exclude_id` on edits so a record doesn't collide with itself.
- **Import/export** (`/import/csv`, `/import/json`, `/export/*`) requires exactly these columns: `nim, nama, email, prodi, angkatan, ipk, no_telp, alamat`. Imports run each row through the same `Validator` + `nim_exists` checks and report per-row failures.
- **Email action** (`/mahasiswa/email/<id>`) is a per-student action surfaced from the list and detail pages; it opens a compose page pre-addressed to that student's recorded email and sends via `EmailSender`.
- **`search_log`** records every search (algorithm, duration, step count, complexity) for the build-log page; users can attach `komentar` to entries.

### Templates

Jinja templates extend `base.html`, which holds the entire CSS design system (cream/red "Suzuran" theme, sidebar nav, toast alerts) inline in a `<style>` block — there are no separate CSS/JS asset files. Reuse the existing classes (`card-dark`, `btn-accent`, `btn-ghost`, `form-control-dark`, `form-label-dark`, `badge-nim`, `page-header`, etc.) rather than introducing new styling. Per-student pages live under `templates/mahasiswa/`.

### Deployment note

On Render free tier the instance spins down after idle and the SQLite file is ephemeral — **data resets on each deploy**. Persistent storage would require a paid plan or migrating off SQLite.
