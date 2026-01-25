"""
MGI Singapore CEC Equipment Booking System
"""
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime
import json

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Configuration
DATABASE = 'bookings.db'
EQUIPMENT_PHOTOS_DIR = 'Equipment Photos'

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
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database"""
    conn = get_db()
    cursor = conn.cursor()
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

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
    conn = get_db()
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
    conn.close()
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
    equipment_id = request.args.get('equipment_id')

    conn = get_db()
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
    conn.close()

    return jsonify(bookings)

@app.route('/api/bookings', methods=['POST'])
def create_booking():
    """Create a new booking"""
    data = request.json

    required_fields = ['equipment_id', 'equipment_name', 'category',
                      'user_name', 'affiliation', 'booking_date',
                      'start_time', 'end_time']

    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing field: {field}'}), 400

    # Check for conflicts
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM bookings
        WHERE equipment_id = ?
        AND booking_date = ?
        AND ((start_time <= ? AND end_time > ?)
             OR (start_time < ? AND end_time >= ?)
             OR (start_time >= ? AND end_time <= ?))
    ''', (data['equipment_id'], data['booking_date'],
          data['start_time'], data['start_time'],
          data['end_time'], data['end_time'],
          data['start_time'], data['end_time']))

    conflict = cursor.fetchone()
    if conflict:
        conn.close()
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

    conn.commit()
    booking_id = cursor.lastrowid
    conn.close()

    return jsonify({'success': True, 'booking_id': booking_id}), 201

@app.route('/api/bookings/<int:booking_id>', methods=['DELETE'])
def delete_booking(booking_id):
    """Delete a booking"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM bookings WHERE id = ?', (booking_id,))
    conn.commit()
    conn.close()

    return jsonify({'success': True})

@app.route('/equipment-photos/<path:filename>')
def serve_equipment_photo(filename):
    """Serve equipment photos"""
    return send_from_directory(EQUIPMENT_PHOTOS_DIR, filename)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8118, debug=False)
