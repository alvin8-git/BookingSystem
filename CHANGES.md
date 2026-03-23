# Changelog

All notable changes to the CEC Equipment Booking System.

---

## v1.3.0 — 2026-03-23

### Accessibility
- Fixed muted text colour contrast: `#6c757d` → `#5a6472` (passes WCAG AA ~4.6:1 on white)
- Added `aria-label="Toggle navigation"` to navbar toggler
- Added `aria-label="Close"` to all `btn-close` buttons
- Added `aria-label="Cancel this booking"` to delete booking button
- Navbar active state applied via `request.path` in `base.html`

### UX — Interactions
- Replaced native `confirm()` dialog with Bootstrap `#confirmDeleteModal` (red header, "Yes, Cancel Booking" / "Go Back")
- Submit button shows spinner + "Confirming…" and is disabled during form submission; restores on success or error
- Calendar event click gives visual feedback (opacity 0.6, scale 0.97); resets when modal opens

### UX — Mobile
- Calendar initial view switches to `timeGridDay` on screens < 768px; `windowResize` callback keeps it in sync on rotation
- Sticky booking form (`position: sticky`) disabled on mobile to prevent overlap with calendar

### UX — Content & Layout
- "Recent Bookings" heading on home page renamed to "Upcoming Bookings"; icon changed to `fa-calendar-alt`
- SGT (UTC+8) timezone note added below submit button
- Empty states with icon + guidance text added to calendar (no events) and bookings list (no upcoming)
- Upcoming bookings count badge injected into card header after list loads; "Showing 10 of N" note when > 10
- Equipment name shown inside overlay on hover (above "Book Now" button)
- Form fields grouped into "Who" (name, affiliation) and "When" (dates, times) sections with labels
- Hero padding reduced: `80px` → `48px` desktop, `50px` → `30px` mobile; heading `display-4` → `display-5`; "Browse Equipment" CTA button removed
- Back button moved into coloured category/booking page header; dedicated bottom back-button sections removed

### Files Changed
- `templates/booking.html`
- `templates/base.html`
- `templates/index.html`
- `templates/category.html`
- `static/css/style.css`

---

## v1.2.0 — 2025

- Multi-day booking support with start/end dates
- Backdated bookings for past dates
- Multi-day conflict detection
- Fixed booking page stall caused by JS syntax error
- Fixed API response format mismatch

---

## v1.1.1 — 2025

- Automatic equipment photo detection and sync
- Equipment registry with file hash change tracking
- Equipment management scripts (`deploy.sh update/sync`, `update_equipment.sh`)

---

## v1.1.0 — 2025

- Production deployment with Gunicorn and Nginx
- systemd service integration
- Database optimisation (WAL mode, indexing)
- Security headers and CORS

---

## v1.0.0 — 2025

- Initial release with core booking functionality
