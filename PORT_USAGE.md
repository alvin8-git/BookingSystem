# Port Usage Summary

## Current Port Allocation

### MGI Singapore CEC Equipment Booking System
- **Development Server**: Port 8118 
  - Flask development server
  - Currently running: ✅
  - File: `/data/alvin/BookingSystem/app.py`

- **Production Server**: Port 8001
  - Gunicorn WSGI + Nginx reverse proxy
  - Available for deployment: ✅
  - Config: `/data/alvin/BookingSystem/gunicorn.conf.py`

### Freezer Inventory System
- **Development Server**: Port 8888
  - Flask development server
  - Location: `/home/alvin/Inventory/`

- **Production Server**: Port 8000
  - Gunicorn WSGI + Nginx reverse proxy
  - Currently running: ✅
  - Config: `/home/alvin/Inventory/gunicorn.conf.py`

## Port Conflicts - RESOLVED ✅

### Original Issue:
- BookingSystem was incorrectly configured to use port 8888 for production
- This would conflict with Inventory development server

### Resolution Applied:
- Changed BookingSystem production port from 8888 → 8001
- Updated all configuration files:
  - `gunicorn.conf.py`
  - `deploy.sh`
  - `nginx.conf`
  - `DEPLOYMENT.md`

## Deployment Commands

### Start BookingSystem Production:
```bash
cd /data/alvin/BookingSystem
./deploy.sh start
```

### Start Inventory Production (if needed):
```bash
cd /home/alvin/Inventory
./deploy.sh start
```

## Access URLs

### BookingSystem:
- Development: http://192.168.1.168:8118
- Production: http://192.168.1.168:8001
- Nginx: http://192.168.1.168 (if nginx configured for port 8001)

### Inventory:
- Development: http://192.168.1.168:8888
- Production: http://192.168.1.168:8000
- Nginx: http://192.168.1.168 (if nginx configured for port 8000)

## Network Diagram
```
Internet → Nginx (port 80) → Backend Services
                          ├─ BookingSystem:8001
                          └─ Inventory:8000

Direct Access:
├─ BookingSystem Development:8118
├─ BookingSystem Production:8001
├─ Inventory Development:8888
└─ Inventory Production:8000
```