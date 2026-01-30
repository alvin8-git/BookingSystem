"""
MGI Singapore CEC Equipment Booking System v1.1.0
Production-ready equipment booking system with WSGI deployment
"""
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime, time
import json
import re
import logging
from werkzeug.exceptions import BadRequest, NotFound, Conflict, InternalServerError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Configure logging
log_level = getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper())
log_file = os.getenv('LOG_FILE', 'server.log')

logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration from environment variables
DATABASE = os.getenv('DATABASE_PATH', 'bookings.db')
EQUIPMENT_PHOTOS_DIR = os.getenv('EQUIPMENT_PHOTOS_DIR', 'Equipment Photos')
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 8118))
DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

# Booking configuration
MIN_BOOKING_DURATION = int(os.getenv('MIN_BOOKING_DURATION_MINUTES', 15))
MAX_BOOKING_DURATION = int(os.getenv('MAX_BOOKING_DURATION_HOURS', 8)) * 60  # Convert to minutes
BUSINESS_HOURS_START = os.getenv('BUSINESS_HOURS_START', '07:00')
BUSINESS_HOURS_END = os.getenv('BUSINESS_HOURS_END', '22:00')

# Validation patterns
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
NAME_PATTERN = re.compile(r'^[a-zA-Z\s\-\.\']+$')

def validate_booking_data(data):
    """Validate booking data server-side"""
    errors = []
    booking_date = None
    
    # Required fields validation
    required_fields = ['equipment_id', 'equipment_name', 'category',
                      'user_name', 'affiliation', 'booking_date',
                      'start_time', 'end_time']
    
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f'{field} is required')
    
    if errors:
        return errors
    
    # Name validation
    if not NAME_PATTERN.match(data['user_name']) or len(data['user_name'].strip()) < 2:
        errors.append('Invalid user name')
    
    # Affiliation validation
    if len(data['affiliation'].strip()) < 3:
        errors.append('Affiliation must be at least 3 characters')
    
    # Date validation
    try:
        booking_date = datetime.strptime(data['booking_date'], '%Y-%m-%d').date()
        if booking_date < datetime.now().date():
            errors.append('Booking date cannot be in the past')
    except ValueError:
        errors.append('Invalid date format')
    
    # Time validation
    try:
        start_time = datetime.strptime(data['start_time'], '%H:%M').time()
        end_time = datetime.strptime(data['end_time'], '%H:%M').time()
        
        if start_time >= end_time:
            errors.append('End time must be after start time')
            
        # Business hours validation
        business_start = datetime.strptime(BUSINESS_HOURS_START, '%H:%M').time()
        business_end = datetime.strptime(BUSINESS_HOURS_END, '%H:%M').time()
        if start_time < business_start or end_time > business_end:
            errors.append(f'Bookings must be between {BUSINESS_HOURS_START} and {BUSINESS_HOURS_END}')
            
        # Minimum booking duration
        if booking_date:
            duration_minutes = (datetime.combine(booking_date, end_time) - 
                               datetime.combine(booking_date, start_time)).total_seconds() / 60
            if duration_minutes < MIN_BOOKING_DURATION:
                errors.append(f'Minimum booking duration is {MIN_BOOKING_DURATION} minutes')
                
            # Maximum booking duration
            if duration_minutes > MAX_BOOKING_DURATION:
                errors.append(f'Maximum booking duration is {MAX_BOOKING_DURATION // 60} hours')
            
    except ValueError:
        errors.append('Invalid time format')
    
    # Category validation
    if data['category'] not in CATEGORIES:
        errors.append('Invalid category')
    
    return errors

# Category mapping
CATEGORIES = {
    'sequencing': {
        'name': 'Sequencing',
        'folder': 'Sequencing',
        'color': '#0066cc',
        'icon': 'fa-dna',
        'description': 'High-throughput DNA/RNA sequencing platforms'
    },
    'sample_prep': {
        'name': 'Sample Preparation',
        'folder': 'Sample Prep',
        'color': '#28a745',
        'icon': 'fa-flask',
        'description': 'Automated sample preparation systems'
    },
    'stomics': {
        'name': 'STOmics',
        'folder': 'STOmics',
        'color': '#6f42c1',
        'icon': 'fa-microscope',
        'description': 'Spatial transcriptomics and imaging solutions'
    }
}

def get_db():
    """Get database connection with optimized settings"""
    conn = sqlite3.connect(
        DATABASE,
        timeout=30.0,  # Longer timeout for concurrent access
        check_same_thread=False
    )
    conn.row_factory = sqlite3.Row
    
    # Enable WAL mode for better concurrency
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA synchronous=NORMAL')
    conn.execute('PRAGMA cache_size=10000')
    conn.execute('PRAGMA temp_store=MEMORY')
    
    return conn

class DatabaseManager:
    """Context manager for database operations"""
    def __enter__(self):
        self.conn = get_db()
        return self.conn
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.conn.rollback()
        else:
            self.conn.commit()
        self.conn.close()

def init_db():
    """Initialize the database with optimized schema and indexes"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Create bookings table with proper constraints
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipment_id TEXT NOT NULL,
            equipment_name TEXT NOT NULL,
            category TEXT NOT NULL,
            user_name TEXT NOT NULL,
            affiliation TEXT NOT NULL,
            booking_date DATE NOT NULL,
            start_time TIME NOT NULL,
            end_time TIME NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CHECK (start_time < end_time),
            CHECK (booking_date >= date('now'))
        )
    ''')
    
    # Create indexes for performance optimization
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_bookings_equipment_date 
        ON bookings(equipment_id, booking_date)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_bookings_date_time 
        ON bookings(booking_date, start_time, end_time)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_bookings_category 
        ON bookings(category)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_bookings_created_at 
        ON bookings(created_at DESC)
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Database initialized with optimized schema and indexes")

def get_equipment_list(category_key):
    """Get list of equipment from photos directory"""
    if category_key not in CATEGORIES:
        return []

    folder = CATEGORIES[category_key]['folder']
    folder_path = os.path.join(EQUIPMENT_PHOTOS_DIR, folder)

    if not os.path.exists(folder_path):
        return []

    equipment = []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.avif')):
            name = os.path.splitext(filename)[0]
            equipment_id = name.lower().replace(' ', '_').replace('+', 'plus')
            equipment.append({
                'id': equipment_id,
                'name': name,
                'image': filename,
                'category': category_key
            })

    return sorted(equipment, key=lambda x: x['name'])

def get_recent_bookings(category_key=None, limit=5):
    """Get recent bookings, optionally filtered by category"""
    with DatabaseManager() as conn:
        cursor = conn.cursor()

        if category_key:
            cursor.execute('''
                SELECT * FROM bookings
                WHERE category = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (category_key, limit))
        else:
            cursor.execute('''
                SELECT * FROM bookings
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))

        bookings = [dict(row) for row in cursor.fetchall()]
        return bookings

@app.route('/')
def index():
    """Landing page with category cards"""
    categories_data = []
    for key, cat in CATEGORIES.items():
        equipment = get_equipment_list(key)
        recent_bookings = get_recent_bookings(key, 5)
        categories_data.append({
            'key': key,
            'name': cat['name'],
            'color': cat['color'],
            'icon': cat['icon'],
            'description': cat['description'],
            'equipment_count': len(equipment),
            'recent_bookings': recent_bookings
        })

    return render_template('index.html', categories=categories_data)

@app.route('/category/<category_key>')
def category_page(category_key):
    """Category page showing all equipment"""
    if category_key not in CATEGORIES:
        return "Category not found", 404

    category = CATEGORIES[category_key]
    equipment = get_equipment_list(category_key)

    return render_template('category.html',
                         category_key=category_key,
                         category=category,
                         equipment=equipment)

@app.route('/book/<category_key>/<equipment_id>')
def booking_page(category_key, equipment_id):
    """Booking page for specific equipment"""
    if category_key not in CATEGORIES:
        return "Category not found", 404

    equipment_list = get_equipment_list(category_key)
    equipment = next((e for e in equipment_list if e['id'] == equipment_id), None)

    if not equipment:
        return "Equipment not found", 404

    category = CATEGORIES[category_key]

    return render_template('booking.html',
                         category_key=category_key,
                         category=category,
                         equipment=equipment)

@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    """Get bookings for a specific equipment"""
    try:
        equipment_id = request.args.get('equipment_id')
        
        with DatabaseManager() as conn:
            cursor = conn.cursor()

            if equipment_id:
                cursor.execute('''
                    SELECT * FROM bookings
                    WHERE equipment_id = ?
                    ORDER BY booking_date, start_time
                ''', (equipment_id,))
            else:
                cursor.execute('''
                    SELECT * FROM bookings
                    ORDER BY booking_date, start_time
                ''')

            bookings = [dict(row) for row in cursor.fetchall()]
            return jsonify({'success': True, 'data': bookings})
                
    except sqlite3.Error as e:
        logger.error(f"Database error fetching bookings: {e}")
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        logger.error(f"Unexpected error fetching bookings: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/bookings', methods=['POST'])
def create_booking():
    """Create a new booking"""
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
            
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate input data
        validation_errors = validate_booking_data(data)
        if validation_errors:
            return jsonify({'error': 'Validation failed', 'details': validation_errors}), 400

        # Check for conflicts and create booking
        with DatabaseManager() as conn:
            cursor = conn.cursor()

            # Optimized conflict detection
            cursor.execute('''
                SELECT id FROM bookings
                WHERE equipment_id = ? AND booking_date = ?
                AND NOT (end_time <= ? OR start_time >= ?)
            ''', (data['equipment_id'], data['booking_date'],
                  data['start_time'], data['end_time']))

            conflict = cursor.fetchone()
            if conflict:
                return jsonify({'error': 'Time slot already booked'}), 409

            # Create booking
            cursor.execute('''
                INSERT INTO bookings (equipment_id, equipment_name, category,
                                    user_name, affiliation, booking_date,
                                    start_time, end_time, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (data['equipment_id'], data['equipment_name'], data['category'],
                  data['user_name'], data['affiliation'], data['booking_date'],
                  data['start_time'], data['end_time'], data.get('notes', '')))

            booking_id = cursor.lastrowid
            
            logger.info(f"Created booking {booking_id} for {data['equipment_name']} by {data['user_name']}")
            
            return jsonify({
                'success': True, 
                'booking_id': booking_id,
                'message': 'Booking created successfully'
            }), 201

    except sqlite3.Error as e:
        logger.error(f"Database error creating booking: {e}")
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        logger.error(f"Unexpected error creating booking: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/bookings/<int:booking_id>', methods=['DELETE'])
def delete_booking(booking_id):
    """Delete a booking"""
    try:
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            
            # Check if booking exists first
            cursor.execute('SELECT * FROM bookings WHERE id = ?', (booking_id,))
            booking = cursor.fetchone()
            
            if not booking:
                return jsonify({'error': 'Booking not found'}), 404
            
            cursor.execute('DELETE FROM bookings WHERE id = ?', (booking_id,))
            
            logger.info(f"Deleted booking {booking_id}")
            return jsonify({'success': True, 'message': 'Booking cancelled successfully'})
                
    except sqlite3.Error as e:
        logger.error(f"Database error deleting booking {booking_id}: {e}")
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        logger.error(f"Unexpected error deleting booking {booking_id}: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        with DatabaseManager() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM bookings')
            count = cursor.fetchone()[0]
            
            return jsonify({
                'status': 'healthy',
                'version': '1.1.0',
                'database': 'connected',
                'total_bookings': count,
                'config': {
                    'min_booking_duration': MIN_BOOKING_DURATION,
                    'max_booking_duration_hours': MAX_BOOKING_DURATION // 60,
                    'business_hours': f"{BUSINESS_HOURS_START} - {BUSINESS_HOURS_END}"
                }
            })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/equipment-photos/<path:filename>')
def serve_equipment_photo(filename):
    """Serve equipment photos"""
    return send_from_directory(EQUIPMENT_PHOTOS_DIR, filename)

if __name__ == '__main__':
    init_db()
    logger.info(f"Starting booking system on {HOST}:{PORT} (debug: {DEBUG})")
    app.run(host=HOST, port=PORT, debug=DEBUG)
