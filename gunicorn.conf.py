# Gunicorn configuration for production
import multiprocessing

# Server socket - Using port 8001 for BookingSystem (port 8000/8888 used by Inventory)
bind = "192.168.1.168:8001"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart settings
max_requests = 1000
max_requests_jitter = 100
preload_app = True

# Logging
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "booking_system"

# Server mechanics
daemon = False
pidfile = "/tmp/booking_system.pid"
user = None
group = None

# SSL (if needed)
# keyfile = "/path/to/ssl/key.pem"
# certfile = "/path/to/ssl/cert.pem"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190