# MGI Singapore CEC Equipment Booking System

![Version](https://img.shields.io/badge/version-1.4.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-WAL_mode-003B57?logo=sqlite&logoColor=white)
![Platform](https://img.shields.io/badge/platform-Linux-lightgrey?logo=linux)
![License](https://img.shields.io/badge/license-Proprietary-red)

> Web-based equipment booking system for managing laboratory reservations across Sequencing, Sample Preparation, and STOmics categories. Built with Flask, SQLite, and Bootstrap. Deployed with Gunicorn and Nginx.

---

## Table of Contents

- [Quick Start](#quick-start)
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Managing Equipment](#managing-equipment)
- [Sequencer Versions](#sequencer-versions)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)
- [Version History](#version-history)
- [License](#license)

---

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/alvin8-git/BookingSystem.git && cd BookingSystem
pip install -r requirements.txt

# 2. Configure
cp .env.example .env

# 3. Initialize database and sync equipment
python3 -c "from app import init_db; init_db()"
./deploy.sh update

# 4. Run (development)
python3 app.py
# → http://localhost:8118

# 4. Run (production)
./deploy.sh start
# → http://<server-ip>:8001
```

---

## Features

| Feature | Details |
|---|---|
| **Equipment browsing** | Sequencing, Sample Prep, and STOmics categories |
| **Version tracking** | Editable firmware/software version beside each sequencer; visible on category and booking pages |
| **Multi-day bookings** | Start and end dates for bookings spanning multiple days |
| **Backdated bookings** | Record historical equipment usage for past dates |
| **Conflict detection** | Prevents double-bookings across overlapping date/time ranges |
| **Equipment photo sync** | Auto-detects photos from folders and registers equipment |
| **Calendar view** | FullCalendar integration; auto-switches to day view on mobile |
| **Accessible UI** | WCAG AA contrast, `aria-label` on interactive elements, keyboard-navigable |
| **Loading feedback** | Spinner on form submit, Bootstrap confirmation modal for cancellations |
| **Responsive design** | Desktop and mobile; sticky form disabled on small screens |
| **Production-ready** | Gunicorn + Nginx + systemd service management |

---

## Installation

### Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.8+ |
| OS | Linux (Ubuntu/Debian recommended) |
| RAM | 512 MB minimum |
| Nginx | Optional (production) |
| systemd | Optional (production) |

### Steps

**1. Clone the repository**

```bash
git clone https://github.com/alvin8-git/BookingSystem.git
cd BookingSystem
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

Installs: `flask`, `flask-cors`, `python-dotenv`, `gunicorn`

**3. Configure environment**

```bash
cp .env.example .env
# Edit .env as needed — see Configuration section
```

**4. Initialize the database**

```bash
python3 -c "from app import init_db; init_db()"
```

Creates `bookings.db` with all tables, indexes, and runs any pending migrations automatically.

**5. Set up equipment photos**

```
Equipment Photos/
├── Sequencing/      ← sequencer images
├── Sample Prep/     ← sample prep instrument images
└── STOmics/         ← STOmics instrument images
```

**6. Sync equipment registry**

```bash
./deploy.sh update
```

---

## Configuration

All settings are read from `.env` (copy from `.env.example`):

```ini
# Flask
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-secret-key-here

# Server
HOST=0.0.0.0
PORT=8118                         # dev port; Gunicorn uses 8001

# Database
DATABASE_PATH=bookings.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=server.log

# Booking rules
MIN_BOOKING_DURATION_MINUTES=15
MAX_BOOKING_DURATION_HOURS=8
BUSINESS_HOURS_START=07:00
BUSINESS_HOURS_END=22:00

# Equipment
EQUIPMENT_PHOTOS_DIR=Equipment Photos
```

### Port Allocation

| Environment | Port |
|---|---|
| Development (Flask) | 8118 |
| Production (Gunicorn) | 8001 |

---

## Deployment

### Option A — Deploy script (recommended)

```bash
./deploy.sh start      # start Gunicorn
./deploy.sh stop       # stop
./deploy.sh restart    # restart
./deploy.sh status     # check if running
./deploy.sh logs       # view recent logs
./deploy.sh sync       # update equipment registry and restart
```

### Option B — systemd service

```bash
sudo cp booking-system.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable booking-system
sudo systemctl start booking-system
```

Manage with: `systemctl status | restart | stop booking-system`

### Option C — Nginx reverse proxy

```bash
sudo cp nginx.conf /etc/nginx/sites-available/booking-system
sudo ln -s /etc/nginx/sites-available/booking-system /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### Updating the application

```bash
./deploy.sh stop
git pull origin main
pip install -r requirements.txt
python3 -c "from app import init_db; init_db()"   # applies migrations
./deploy.sh sync
```

> **Backup first:** `cp bookings.db bookings_backup_$(date +%Y%m%d).db`

---

## Managing Equipment

Equipment is driven entirely by image files in `Equipment Photos/`. The filename (without extension) becomes the display name; the subfolder determines the category.

### Naming convention

| File path | Display name | Category |
|---|---|---|
| `Equipment Photos/Sequencing/DNBSEQ-G400.avif` | DNBSEQ-G400 | Sequencing |
| `Equipment Photos/Sample Prep/MGISP-100.png` | MGISP-100 | Sample Prep |
| `Equipment Photos/STOmics/Leica DM6 Microscope.avif` | Leica DM6 Microscope | STOmics |

Supported formats: `.png` `.jpg` `.jpeg` `.webp` `.avif`

### Add equipment

```bash
cp DNBSEQ-T20.png "Equipment Photos/Sequencing/"
./deploy.sh sync          # updates registry and restarts
```

### Remove equipment

```bash
rm "Equipment Photos/Sample Prep/Old Equipment.png"
./deploy.sh sync          # marks inactive; existing bookings preserved
```

### Replace a photo

Keep the same filename — the system detects file content changes via MD5 hash.

```bash
cp new-photo.png "Equipment Photos/Sequencing/DNBSEQ-G400.png"
./deploy.sh sync
```

> **Note:** Renaming a file is treated as removal + addition. Existing bookings referencing the old name are preserved.

---

## Sequencer Versions

Firmware/software versions are stored in the equipment registry and displayed on the category and booking pages. They are pre-seeded on first run and can be edited inline on each sequencer's booking page (pencil icon beside the name).

| Sequencer | Version |
|---|---|
| DNBSEQ-E25 | ECR2.5.1 *(requires update to ECR2.5.2)* |
| DNBSEQ-G50 | ECR6.0 *(requires update to ECR7.0)* |
| DNBSEQ-G99 | ECR4.0v2 |
| DNBSEQ-G400 | ECR7.2 |
| G100-ER (×2) | G100-E V1.4.1.17 |
| G400-ER | G400-E V1.2.1.1 |
| DNBSEQ-T7 | ECR5.1 |
| DNBSEQ-T1+ | ECR1.0 |

To update a version via API:

```bash
curl -X PUT http://localhost:8001/api/equipment/dnbseq-e25/version \
     -H "Content-Type: application/json" \
     -d '{"version": "ECR2.5.2"}'
```

---

## API Reference

### Bookings

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/bookings?equipment_id=<id>` | List bookings (filter by equipment) |
| `POST` | `/api/bookings` | Create a booking |
| `DELETE` | `/api/bookings/<id>` | Cancel a booking |

**POST `/api/bookings` body:**

```json
{
  "equipment_id": "dnbseq-e25",
  "equipment_name": "DNBSEQ-E25",
  "category": "sequencing",
  "user_name": "Jane Doe",
  "affiliation": "NUS Lab",
  "booking_date": "2026-05-20",
  "end_date": "2026-05-20",
  "start_time": "09:00",
  "end_time": "12:00",
  "notes": ""
}
```

### Equipment

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/equipment` | List all registered equipment |
| `POST` | `/api/equipment/sync` | Trigger photo-folder sync |
| `PUT` | `/api/equipment/<id>/version` | Update version string |

### System

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check — DB status, booking count, config |
| `GET` | `/equipment-photos/<path>` | Serve equipment photo |

### Pages

| Endpoint | Description |
|---|---|
| `/` | Home — category overview |
| `/category/<key>` | Equipment grid (`sequencing` / `sample_prep` / `stomics`) |
| `/book/<key>/<equipment_id>` | Booking calendar + form for one piece of equipment |

---

## Troubleshooting

<details>
<summary><strong>Port already in use</strong></summary>

```bash
sudo lsof -i :8001
sudo kill <PID>
```
</details>

<details>
<summary><strong>Equipment not showing up</strong></summary>

1. Confirm the image is in the correct `Equipment Photos/<Category>/` folder.
2. Confirm the extension is `.png`, `.jpg`, `.jpeg`, `.webp`, or `.avif`.
3. Run `./deploy.sh sync`.
4. Check `tail -f logs/equipment_update.log`.
</details>

<details>
<summary><strong>Database errors / reset</strong></summary>

```bash
# Check permissions
ls -la bookings.db

# Full reset (WARNING: deletes all bookings)
cp bookings.db bookings_backup_$(date +%Y%m%d).db
rm bookings.db
python3 -c "from app import init_db; init_db()"
./deploy.sh sync
```
</details>

<details>
<summary><strong>Enable debug logging</strong></summary>

```bash
export LOG_LEVEL=DEBUG
./deploy.sh restart
tail -f logs/error.log
```
</details>

<details>
<summary><strong>Health check</strong></summary>

```bash
curl http://localhost:8001/api/health
```
</details>

---

## Version History

| Version | Date | Highlights |
|---|---|---|
| **v1.4.0** | 2026-05-14 | Equipment version tracking; editable inline on booking page; pre-seeded for all sequencers |
| v1.3.0 | 2026-03-23 | Accessibility (WCAG AA), mobile calendar view, Bootstrap confirm modal, loading spinner, empty states |
| v1.2.0 | 2025 | Multi-day bookings, backdated bookings, multi-day conflict detection |
| v1.1.1 | 2025 | Equipment photo auto-sync, file hash change tracking |
| v1.1.0 | 2025 | Gunicorn + Nginx deployment, systemd integration, WAL mode, security headers |
| v1.0.0 | 2025 | Initial release |

Full changelog: [CHANGES.md](CHANGES.md)

---

## License

Proprietary software. MGI Singapore CEC. All rights reserved.
