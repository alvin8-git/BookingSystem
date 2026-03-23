# TODO

Tracked improvements and known issues for the CEC Equipment Booking System.

---

## In Progress

_Nothing currently in progress._

---

## Backlog

### Authentication & Access Control
- [ ] Add simple PIN or password protection for booking cancellations (prevent unauthorized deletes)
- [ ] Optional admin view to see all bookings across all equipment on one calendar

### Notifications
- [ ] Email confirmation on booking creation (optional SMTP config)
- [ ] Daily digest of upcoming bookings for lab managers

### Booking UX
- [ ] Allow users to edit an existing booking (change time/date) without cancelling and re-booking
- [ ] Recurring bookings (e.g., every Tuesday 9–11am)
- [ ] "Book again" shortcut that pre-fills the form with the last booking's details

### Calendar
- [ ] Color-code events by user or affiliation for easier visual scanning
- [ ] Export calendar to `.ics` / Google Calendar

### Equipment Management
- [ ] Equipment description field (shown on booking page)
- [ ] Equipment status flag (available / under maintenance / retired) visible to users
- [ ] Bulk equipment import from CSV

### Operations
- [ ] Automated daily `bookings.db` backup to a separate directory
- [ ] Log rotation for `logs/` directory
- [ ] `/api/health` endpoint to include gunicorn worker count and uptime

### Accessibility
- [ ] Full keyboard navigation test and fixes for FullCalendar toolbar
- [ ] Screen reader test with NVDA/JAWS

---

## Completed

- [x] v1.3.0 — Loading spinner on submit, Bootstrap confirmation modal, WCAG AA contrast, aria-labels, mobile calendar day view, sticky form fix, empty states, timezone indicator, form grouping, hero reduction, back button relocation, navbar active state, bookings count badge
- [x] v1.2.0 — Multi-day bookings, backdated bookings, conflict detection fixes
- [x] v1.1.1 — Equipment photo auto-sync, hash-based change detection
- [x] v1.1.0 — Gunicorn + Nginx production deployment, systemd, WAL mode
- [x] v1.0.0 — Core booking system
