# MGI Singapore CEC Equipment Booking System

A comprehensive web-based equipment booking system for managing laboratory equipment reservations across multiple categories including Sequencing, Sample Preparation, and STOmics equipment.

## 🚀 Features

### Core Functionality
- **Equipment Management**: Browse and book laboratory equipment by category
- **Real-time Availability**: View current bookings and time slot availability
- **User-friendly Interface**: Intuitive booking interface with photo previews
- **Conflict Prevention**: Automatic detection of double-bookings
- **Business Hours**: Configurable booking time restrictions
- **Validation**: Comprehensive input validation and error handling

### Categories
- **Sequencing**: High-throughput DNA/RNA sequencing platforms
- **Sample Preparation**: Automated sample preparation systems  
- **STOmics**: Spatial transcriptomics and imaging solutions

### Technical Features
- RESTful API endpoints
- SQLite database with optimized indexing
- File-based equipment photo management
- Responsive web design
- Production-ready deployment with Gunicorn
- Nginx reverse proxy support
- Comprehensive logging system

## 📋 System Requirements

### Runtime Dependencies
- **Python**: 3.8 or higher
- **Operating System**: Linux (Ubuntu/Debian recommended)
- **Memory**: Minimum 512MB RAM
- **Storage**: 100MB+ for application and data

### Production Dependencies
- **Gunicorn**: WSGI HTTP Server
- **Nginx**: Reverse proxy (recommended)
- **Systemd**: Service management (Linux)

## 🛠️ Installation

### 1. Clone or Deploy the Application
```bash
# Navigate to the application directory
cd /data/alvin/BookingSystem
```

### 2. Set Up Python Environment
```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Or use system-wide installation
pip3 install -r requirements.txt
```

### 3. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables as needed
nano .env
```

### 4. Initialize Database
```bash
# Initialize SQLite database with optimized schema
python3 -c "from app import init_db; init_db()"
```

### 5. Set Up Equipment Photos
```bash
# Ensure equipment photos are properly organized
# Structure: Equipment Photos/
#   ├── Sequencing/
#   ├── Sample Prep/
#   └── STOmics/
ls "Equipment Photos"
```

## 🏃‍♂️ Running the Application

### Development Mode
```bash
# Run Flask development server
python3 app.py

# Or use the configured port (8118)
python3 -c "
import os
os.environ['FLASK_DEBUG'] = 'True'
os.environ['PORT'] = '8118'
from app import app, init_db
init_db()
app.run(host='0.0.0.0', port=8118, debug=True)
"
```

Access the application at: http://192.168.1.168:8118

### Production Deployment
#### Option 1: Using Deployment Script (Recommended)
```bash
# Start production server
./deploy.sh start

# Check status
./deploy.sh status

# View logs
./deploy.sh logs

# Stop server
./deploy.sh stop

# Restart server
./deploy.sh restart
```

#### Option 2: Using Gunicorn Directly
```bash
# Start with Gunicorn
gunicorn --config gunicorn.conf.py wsgi:app
```

#### Option 3: Systemd Service
```bash
# Install as system service
sudo cp booking-system.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable booking-system
sudo systemctl start booking-system
```

## 🌐 Production URLs

### Direct Access
- **Development**: http://192.168.1.168:8118
- **Production**: http://192.168.1.168:8001

### Nginx Reverse Proxy (Recommended)
```bash
# Install nginx configuration
sudo cp nginx.conf /etc/nginx/sites-available/booking-system
sudo ln -s /etc/nginx/sites-available/booking-system /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

Access via Nginx: http://192.168.1.168

## ⚙️ Configuration

### Environment Variables
Create `.env` file with the following variables:

```bash
# Database Configuration
DATABASE_PATH=bookings.db

# Directories
EQUIPMENT_PHOTOS_DIR=Equipment Photos

# Server Configuration
HOST=0.0.0.0
PORT=8118
FLASK_DEBUG=False

# Logging
LOG_LEVEL=INFO
LOG_FILE=server.log

# Booking Rules
MIN_BOOKING_DURATION_MINUTES=15
MAX_BOOKING_DURATION_HOURS=8
BUSINESS_HOURS_START=07:00
BUSINESS_HOURS_END=22:00
```

### Port Configuration
| Environment | Port | Protocol |
|------------|------|----------|
| Development | 8118 | HTTP |
| Production | 8001 | HTTP |
| Inventory Production | 8000 | HTTP (separate system) |
| Inventory Development | 8888 | HTTP (separate system) |

## 📊 API Endpoints

### Booking Management
- `GET /api/bookings` - List all bookings or by equipment
- `POST /api/bookings` - Create new booking
- `DELETE /api/bookings/<id>` - Cancel booking

### System
- `GET /api/health` - Health check endpoint
- `GET /equipment-photos/<path>` - Serve equipment photos

### Web Pages
- `/` - Landing page with category overview
- `/category/<category_key>` - Equipment listing by category
- `/book/<category_key>/<equipment_id>` - Equipment booking page

## 🔧 Maintenance

### Database Management
```bash
# Backup database
cp bookings.db bookings_backup_$(date +%Y%m%d).db

# View database stats
sqlite3 bookings.db ".schema"
sqlite3 bookings.db "SELECT COUNT(*) FROM bookings;"
```

### Log Management
```bash
# View application logs
tail -f server.log

# View production logs
tail -f logs/access.log
tail -f logs/error.log

# Log rotation (add to crontab)
find logs/ -name "*.log" -mtime +30 -delete
```

### System Monitoring
```bash
# Check service status
./deploy.sh status

# Monitor resource usage
htop

# Check port availability
netstat -tlnp | grep -E ':(8001|8118)'
```

## 🆕 Version History

### v1.1.0 (Current)
- **New**: Production deployment with Gunicorn WSGI
- **New**: Nginx reverse proxy configuration
- **New**: Systemd service integration
- **New**: Comprehensive deployment automation
- **Improved**: Database optimization with WAL mode and indexing
- **Improved**: Security headers and CORS configuration
- **Fixed**: Port conflicts with Inventory system
- **Fixed**: Resource cleanup and connection management

### v1.0.0
- **Initial Release**: Core booking functionality
- **Features**: Equipment management, conflict detection, validation
- **Architecture**: Flask development server, SQLite database

## 🔒 Security Features

- Input validation and sanitization
- SQL injection protection with parameterized queries
- CORS configuration for cross-origin requests
- Security headers (X-Frame-Options, X-Content-Type-Options, etc.)
- Access logging and monitoring
- File system access controls

## 🐛 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Check what's using the port
sudo netstat -tlnp | grep :8001
sudo lsof -i :8001

# Kill conflicting process
sudo kill -9 <PID>
```

#### Database Connection Errors
```bash
# Check database file permissions
ls -la bookings.db

# Reinitialize database
rm bookings.db
python3 -c "from app import init_db; init_db()"
```

#### Static Files Not Loading
```bash
# Check file permissions
ls -la static/
ls -la "Equipment Photos/"

# Restart server
./deploy.sh restart
```

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
./deploy.sh restart

# Check detailed logs
tail -f logs/error.log
```

## 📞 Support

### Contact
- **System Administrator**: Use the health check endpoint for status
- **Documentation**: See `DEPLOYMENT.md` for detailed setup instructions

### Health Monitoring
```bash
# Check application health
curl http://192.168.1.168:8001/api/health

# Expected response
{"status": "healthy", "database": "connected", "total_bookings": 0}
```

## 📄 License

This software is proprietary to MGI Singapore CEC. All rights reserved.

---

**Note**: This documentation is for v1.1.0. For version-specific instructions, refer to the version history section.