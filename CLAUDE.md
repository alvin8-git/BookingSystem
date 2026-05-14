# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# context-mode — MANDATORY routing rules

You have context-mode MCP tools available. These rules are NOT optional — they protect your context window from flooding. A single unrouted command can dump 56 KB into context and waste the entire session.

## BLOCKED commands — do NOT attempt these

### curl / wget — BLOCKED
Any Bash command containing `curl` or `wget` is intercepted and replaced with an error message. Do NOT retry.
Instead use:
- `ctx_fetch_and_index(url, source)` to fetch and index web pages
- `ctx_execute(language: "javascript", code: "const r = await fetch(...)")` to run HTTP calls in sandbox

### Inline HTTP — BLOCKED
Any Bash command containing `fetch('http`, `requests.get(`, `requests.post(`, `http.get(`, or `http.request(` is intercepted and replaced with an error message. Do NOT retry with Bash.
Instead use:
- `ctx_execute(language, code)` to run HTTP calls in sandbox — only stdout enters context

### WebFetch — BLOCKED
WebFetch calls are denied entirely. The URL is extracted and you are told to use `ctx_fetch_and_index` instead.
Instead use:
- `ctx_fetch_and_index(url, source)` then `ctx_search(queries)` to query the indexed content

## REDIRECTED tools — use sandbox equivalents

### Bash (>20 lines output)
Bash is ONLY for: `git`, `mkdir`, `rm`, `mv`, `cd`, `ls`, `npm install`, `pip install`, and other short-output commands.
For everything else, use:
- `ctx_batch_execute(commands, queries)` — run multiple commands + search in ONE call
- `ctx_execute(language: "shell", code: "...")` — run in sandbox, only stdout enters context

### Read (for analysis)
If you are reading a file to **Edit** it → Read is correct (Edit needs content in context).
If you are reading to **analyze, explore, or summarize** → use `ctx_execute_file(path, language, code)` instead. Only your printed summary enters context. The raw file content stays in the sandbox.

### Grep (large results)
Grep results can flood context. Use `ctx_execute(language: "shell", code: "grep ...")` to run searches in sandbox. Only your printed summary enters context.

## Tool selection hierarchy

1. **GATHER**: `ctx_batch_execute(commands, queries)` — Primary tool. Runs all commands, auto-indexes output, returns search results. ONE call replaces 30+ individual calls.
2. **FOLLOW-UP**: `ctx_search(queries: ["q1", "q2", ...])` — Query indexed content. Pass ALL questions as array in ONE call.
3. **PROCESSING**: `ctx_execute(language, code)` | `ctx_execute_file(path, language, code)` — Sandbox execution. Only stdout enters context.
4. **WEB**: `ctx_fetch_and_index(url, source)` then `ctx_search(queries)` — Fetch, chunk, index, query. Raw HTML never enters context.
5. **INDEX**: `ctx_index(content, source)` — Store content in FTS5 knowledge base for later search.

## Subagent routing

When spawning subagents (Agent/Task tool), the routing block is automatically injected into their prompt. Bash-type subagents are upgraded to general-purpose so they have access to MCP tools. You do NOT need to manually instruct subagents about context-mode.

## Output constraints

- Keep responses under 500 words.
- Write artifacts (code, configs, PRDs) to FILES — never return them as inline text. Return only: file path + 1-line description.
- When indexing content, use descriptive source labels so others can `ctx_search(source: "label")` later.

## ctx commands

| Command | Action |
|---------|--------|
| `ctx stats` | Call the `ctx_stats` MCP tool and display the full output verbatim |
| `ctx doctor` | Call the `ctx_doctor` MCP tool, run the returned shell command, display as checklist |
| `ctx upgrade` | Call the `ctx_upgrade` MCP tool, run the returned shell command, display as checklist |

---

# Project: MGI Singapore CEC Equipment Booking System

Flask + SQLite web app for booking lab equipment (Sequencing, Sample Prep, STOmics). No authentication — open access by design.

## Commands

```bash
# Development server (port 8118)
python app.py

# Initialize / reset database
python3 -c "from app import init_db; init_db()"

# Sync equipment registry from photo folders
python3 -c "from app import sync_equipment_registry; sync_equipment_registry()"

# Production management via deploy script
./deploy.sh start | stop | restart | status | update-equipment | logs

# Health check
curl http://localhost:8001/api/health
```

There is no test suite. Manual testing via the browser or `/api/health`.

## Architecture

Everything lives in a single file: **`app.py`** (~760 lines). There are no blueprints, no separate models file, no ORM.

**Database** — SQLite (`bookings.db`) with WAL mode. Two tables:
- `equipment_registry` — populated by scanning `Equipment Photos/` subfolders; each row is one piece of equipment identified by a stable `equipment_id` (slug of name + hash)
- `bookings` — user bookings with `booking_date`/`end_date` (multi-day) and `start_time`/`end_time`; no foreign-key constraint to `equipment_registry`

**Equipment categories** — defined in the `CATEGORIES` dict at the top of `app.py`. Each category maps to a subfolder under `Equipment Photos/`. Adding a new category requires updating `CATEGORIES` and creating the folder.

**Equipment sync** — `sync_equipment_registry()` scans `Equipment Photos/<Folder>/` for image files, computes a file hash, and upserts rows into `equipment_registry`. Run this whenever photos are added/renamed/removed.

**Conflict detection** — overlap check via SQL datetime string comparison (ISO format). Multi-day bookings use `COALESCE(end_date, booking_date)`.

**Templates** — Jinja2, extending `templates/base.html`:
- `index.html` — category grid landing page
- `category.html` — equipment list for one category
- `booking.html` — FullCalendar view + booking form for one piece of equipment

**Static** — only `static/css/style.css`; Bootstrap 5 and FullCalendar are loaded from CDN.

## Key routes

| Route | Purpose |
|---|---|
| `GET /` | Category landing page |
| `GET /category/<key>` | Equipment list (key: `sequencing`, `sample_prep`, `stomics`) |
| `GET /book/<category_key>/<equipment_id>` | Booking page + calendar |
| `GET /api/bookings` | List bookings (filterable by `equipment_id`, `date`) |
| `POST /api/bookings` | Create booking (JSON) |
| `DELETE /api/bookings/<id>` | Cancel booking |
| `GET /api/equipment` | Equipment list from registry |
| `POST /api/equipment/sync` | Trigger photo-folder sync |
| `PUT /api/equipment/<id>/version` | Update equipment version string |
| `GET /api/health` | Health check |
| `GET /equipment-photos/<path>` | Serve equipment photos |

## Configuration (`.env`)

| Variable | Default | Notes |
|---|---|---|
| `PORT` | `8118` | Dev port; Gunicorn uses `8001` (set in `gunicorn.conf.py`) |
| `DATABASE_PATH` | `bookings.db` | SQLite file path |
| `EQUIPMENT_PHOTOS_DIR` | `Equipment Photos` | Root folder for equipment images |
| `BUSINESS_HOURS_START/END` | `07:00` / `22:00` | Enforced in booking validation |
| `MIN_BOOKING_DURATION_MINUTES` | `15` | |
| `MAX_BOOKING_DURATION_HOURS` | `8` | |

## Production deployment

- Gunicorn (`gunicorn.conf.py`) on port **8001**; PID at `/tmp/booking_system.pid`
- Nginx reverse proxy (`nginx.conf`) fronts port 8001
- systemd unit: `booking-system.service`
- `deploy.sh` wraps all start/stop/restart/log operations

## Adding equipment

1. Drop an image into the correct `Equipment Photos/<Category>/` subfolder
2. Run `./deploy.sh update-equipment` (or `POST /api/equipment/sync`)
3. The equipment appears immediately — no code changes needed
