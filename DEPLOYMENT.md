# Booking System - Production Deployment Guide

## Overview
This guide covers deploying the MGI Singapore CEC Equipment Booking System in production using Gunicorn WSGI server with Nginx reverse proxy.

## Files Created
- `wsgi.py` - WSGI entry point for production
- `gunicorn.conf.py` - Gunicorn configuration (port 8001)
- `deploy.sh` - Deployment script for managing the application
- `booking-system.service` - Systemd service file
- `nginx.conf` - Nginx configuration for reverse proxy
- `requirements.txt` - Updated with gunicorn dependency

## Port Configuration
- **Development**: Port 8118 (Flask dev server)
- **Production**: Port 8001 (Gunicorn + Nginx)
- **Inventory System**: Ports 8000/8888 (avoid conflicts)

## Deployment Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Using the Deployment Script (Recommended)
```bash
# Start the application
./deploy.sh start

# Check status
./deploy.sh status

# View logs
./deploy.sh logs

# Stop the application
./deploy.sh stop

# Restart the application
./deploy.sh restart
```

### 3. Systemd Service Setup (Alternative)
```bash
# Copy service file
sudo cp booking-system.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable booking-system

# Start service
sudo systemctl start booking-system

# Check status
sudo systemctl status booking-system
```

### 4. Nginx Configuration
```bash
# Copy nginx config
sudo cp nginx.conf /etc/nginx/sites-available/booking-system

# Enable site
sudo ln -s /etc/nginx/sites-available/booking-system /etc/nginx/sites-enabled/

# Test nginx configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

## Production URLs
- **Direct access**: http://192.168.1.168:8001
- **Through Nginx**: http://192.168.1.168 (port 80)

## Security Features
- Security headers configured
- Gzip compression enabled
- Static file caching
- Access logging
- Process isolation with systemd

## Logging
- Application logs: `logs/error.log`, `logs/access.log`
- Systemd logs: `logs/systemd.log`, `logs/systemd_error.log`
- Nginx logs: `/var/log/nginx/access.log`, `/var/log/nginx/error.log`

## Performance Optimizations
- Multiple worker processes (CPU cores × 2 + 1)
- Database WAL mode for better concurrency
- Optimized database indexes
- Static file caching
- Connection pooling

## Monitoring
- Health check endpoint: `/api/health`
- Nginx health check: `/health`

## Troubleshooting
1. Check logs: `./deploy.sh logs`
2. Verify port availability: `netstat -tlnp | grep :8888`
3. Check nginx configuration: `nginx -t`
4. Test database connectivity: Check health endpoint

## Environment Variables
Set these in `.env` file for production:
```
HOST=0.0.0.0
PORT=8118
FLASK_DEBUG=False
LOG_LEVEL=INFO
DATABASE_PATH=bookings.db
EQUIPMENT_PHOTOS_DIR=Equipment Photos
```