# MGI Singapore CEC Equipment Booking System

A web-based equipment booking system for managing laboratory equipment reservations across Sequencing, Sample Preparation, and STOmics categories.

Built with Flask, SQLite, and Bootstrap. Deployed with Gunicorn and Nginx.

---

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Downloading](#downloading)
- [Installation](#installation)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Managing Equipment](#managing-equipment)
- [Updating the Application](#updating-the-application)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)
- [Version History](#version-history)
- [License](#license)

---

## Features

- **Multi-category equipment browsing** — Sequencing, Sample Prep, and STOmics
- **Multi-day bookings** — support for bookings spanning multiple days
- **Backdated bookings** — record historical equipment usage
- **Conflict detection** — prevents double-bookings across date/time ranges
- **Equipment photo sync** — auto-detects photos and registers equipment
- **Calendar view** — interactive calendar powered by FullCalendar
- **Responsive design** — works on desktop and mobile
- **Production-ready** — Gunicorn + Nginx with systemd service management

---

## Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.8+ |
| pip | Latest |
| OS | Linux (Ubuntu/Debian recommended) |
| RAM | 512 MB minimum |
| Disk | 100 MB+ |

**Optional (for production):**

- Nginx (reverse proxy)
- systemd (service management)

---

## Downloading

### Clone from GitHub

```bash
git clone git@github.com:alvin8-git/BookingSystem.git
cd BookingSystem
```

Or using HTTPS:

```bash
git clone https://github.com/alvin8-git/BookingSystem.git
cd BookingSystem
```

---

## Installation

### Step 1: Create a Python virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 2: Install dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `flask` — web framework
- `flask-cors` — cross-origin request support
- `python-dotenv` — environment variable management
- `gunicorn` — production WSGI server

### Step 3: Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` as needed. See [Configuration](#configuration) for all options.

### Step 4: Initialize the database

```bash
python3 -c "from app import init_db; init_db()"
```

This creates `bookings.db` with the required schema (tables for bookings and equipment registry).

### Step 5: Set up equipment photos

Ensure the `Equipment Photos/` directory exists with subdirectories for each category:

```
Equipment Photos/
├── Sequencing/
├── Sample Prep/
└── STOmics/
```

Place equipment images in the appropriate category folder. See [Managing Equipment](#managing-equipment) for naming conventions and detailed instructions.

### Step 6: Sync equipment registry

```bash
./deploy.sh update
```

This scans the photo directories and populates the equipment registry in the database.

---

## Configuration

Create a `.env` file in the project root (or copy from `.env.example`):

```bash
# Flask
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-secret-key-here

# Server
HOST=0.0.0.0
PORT=8118

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

### Port allocation

| Environment | Port | Description |
|---|---|---|
| Development | 8118 | Flask dev server |
| Production | 8001 | Gunicorn |

---

## Deployment

### Option A: Deployment script (recommended)

The `deploy.sh` script manages the Gunicorn production server.

```bash
# Start the server
./deploy.sh start

# Stop the server
./deploy.sh stop

# Restart the server
./deploy.sh restart

# Check status
./deploy.sh status

# View recent logs
./deploy.sh logs
```

The production server runs at `http://<your-server-ip>:8001`.

### Option B: systemd service

For automatic startup on boot:

```bash
# Copy the service file
sudo cp booking-system.service /etc/systemd/system/

# Reload systemd, enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable booking-system
sudo systemctl start booking-system
```

Manage with standard systemd commands:

```bash
sudo systemctl status booking-system
sudo systemctl restart booking-system
sudo systemctl stop booking-system
```

### Option C: Nginx reverse proxy

To serve the application on port 80 behind Nginx:

```bash
sudo cp nginx.conf /etc/nginx/sites-available/booking-system
sudo ln -s /etc/nginx/sites-available/booking-system /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Development mode

For local development and testing:

```bash
python3 app.py
```

Access at `http://localhost:8118`.

---

## Managing Equipment

Equipment in the booking system is driven entirely by image files in the `Equipment Photos/` directory. To add, remove, or update equipment, you modify the photo files and then sync the registry.

### Photo naming conventions

- The **filename** (without extension) becomes the **equipment display name**
- Supported formats: `.png`, `.jpg`, `.jpeg`, `.webp`, `.avif`
- The **subdirectory** determines the **category**

**Example:**

| File path | Display name | Category |
|---|---|---|
| `Equipment Photos/Sequencing/DNBSEQ-G400.avif` | DNBSEQ-G400 | Sequencing |
| `Equipment Photos/Sample Prep/MGISP-100.png` | MGISP-100 | Sample Prep |
| `Equipment Photos/STOmics/Leica DM6 Microscope.avif` | Leica DM6 Microscope | STOmics |

### Adding new equipment

1. **Prepare the photo.** Use a clear product image. Any supported format works.

2. **Name the file.** The filename (minus extension) is what users see. For example, to add an instrument called "DNBSEQ-T20", name the file `DNBSEQ-T20.png`.

3. **Place the file** in the correct category folder:

   ```bash
   cp DNBSEQ-T20.png "Equipment Photos/Sequencing/"
   ```

4. **Stop the service** (if running in production):

   ```bash
   ./deploy.sh stop
   ```

5. **Sync the equipment registry:**

   ```bash
   ./deploy.sh update
   ```

6. **Start the service:**

   ```bash
   ./deploy.sh start
   ```

   Or combine the sync and restart in one command:

   ```bash
   ./deploy.sh sync
   ```

   The `sync` command updates the registry and restarts the server automatically.

7. **Verify.** Open the booking system in your browser and confirm the new equipment appears under the correct category.

### Removing equipment

1. **Delete the photo file** from the category folder:

   ```bash
   rm "Equipment Photos/Sample Prep/Old Equipment.png"
   ```

2. **Sync and restart:**

   ```bash
   ./deploy.sh sync
   ```

   The equipment is marked as inactive in the database. Existing bookings for that equipment are preserved.

### Updating an equipment photo

1. **Replace the image file** (keep the same filename to retain the same equipment entry):

   ```bash
   cp new-photo.png "Equipment Photos/Sequencing/DNBSEQ-G400.png"
   ```

2. **Sync and restart:**

   ```bash
   ./deploy.sh sync
   ```

   The system detects the file change via MD5 hash comparison and updates the registry.

### Renaming equipment

Renaming a file is treated as a removal of the old equipment and addition of a new one. Existing bookings linked to the old name are preserved but will reference the old equipment ID.

### Viewing equipment status

```bash
# Show all registered equipment
./update_equipment.sh status

# Show recent changes
./update_equipment.sh changes
```

---

## Updating the Application

### Pulling the latest changes

```bash
cd /data/alvin/BookingSystem

# Stop the running service
./deploy.sh stop

# Pull updates from GitHub
git pull origin main

# Install any new dependencies
source venv/bin/activate
pip install -r requirements.txt

# Reinitialize the database (applies migrations)
python3 -c "from app import init_db; init_db()"

# Sync equipment registry
./deploy.sh update

# Start the service
./deploy.sh start
```

### Backing up before an update

```bash
# Backup the database
cp bookings.db bookings_backup_$(date +%Y%m%d).db
```

---

## API Reference

### Bookings

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/bookings?equipment_id=<id>` | List bookings (optionally filter by equipment) |
| `POST` | `/api/bookings` | Create a new booking |
| `DELETE` | `/api/bookings/<id>` | Cancel a booking |

### Equipment

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/equipment` | Get equipment list |
| `POST` | `/api/equipment/sync` | Trigger equipment registry sync |

### System

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check (includes version and DB status) |
| `GET` | `/equipment-photos/<path>` | Serve equipment photos |

### Pages

| Endpoint | Description |
|---|---|
| `/` | Landing page with category overview |
| `/category/<category_key>` | Equipment listing by category |
| `/book/<category_key>/<equipment_id>` | Booking page for specific equipment |

---

## Troubleshooting

### Port already in use

```bash
sudo lsof -i :8001
sudo kill <PID>
```

### Database errors

```bash
# Check file permissions
ls -la bookings.db

# Reinitialize (WARNING: deletes all data)
rm bookings.db
python3 -c "from app import init_db; init_db()"
./deploy.sh update
```

### Equipment not showing up

1. Confirm the photo is in the correct folder under `Equipment Photos/`.
2. Confirm the file extension is one of: `.png`, `.jpg`, `.jpeg`, `.webp`, `.avif`.
3. Run `./deploy.sh sync` to update the registry and restart the server.
4. Check the log: `tail -f logs/equipment_update.log`.

### Enable debug logging

```bash
export LOG_LEVEL=DEBUG
./deploy.sh restart
tail -f logs/error.log
```

### Health check

```bash
curl http://localhost:8001/api/health
```

---

## Version History

### v1.2.0 (Current)
- Multi-day booking support with start/end dates
- Backdated bookings for past dates
- Multi-day conflict detection
- Fixed booking page stall caused by JS syntax error
- Fixed API response format mismatch

### v1.1.1
- Automatic equipment photo detection and sync
- Equipment registry with file hash change tracking
- Equipment management scripts (`deploy.sh update/sync`, `update_equipment.sh`)

### v1.1.0
- Production deployment with Gunicorn and Nginx
- systemd service integration
- Database optimization (WAL mode, indexing)
- Security headers and CORS

### v1.0.0
- Initial release with core booking functionality

---

## License

Proprietary software. MGI Singapore CEC. All rights reserved.
