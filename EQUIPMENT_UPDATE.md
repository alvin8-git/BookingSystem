# Equipment Photo Update Guide

## Overview

The Booking System now includes automatic equipment registry management that detects changes in equipment photos and keeps the booking system synchronized with your photo library.

## 🎯 Features

### Photo Change Detection
- **New Equipment**: Automatically detects newly added photos and creates booking entries
- **Removed Equipment**: Marks equipment as inactive when photos are removed
- **Updated Photos**: Detects when photo files are changed (different content)
- **File Hash Verification**: Uses MD5 hashing to detect actual file changes

### Smart Categorization
- Automatically categorizes equipment based on folder structure
- Supports all image formats: `.png`, `.jpg`, `.jpeg`, `.webp`, `.avif`
- Preserves original filenames for display while creating safe equipment IDs

## 🚀 Usage

### Method 1: Using Deployment Script (Recommended)
```bash
# Update equipment registry only
./deploy.sh update

# Update and restart application
./deploy.sh sync
```

### Method 2: Using Dedicated Equipment Script
```bash
# Update equipment registry
./update_equipment.sh update

# Show current equipment status
./update_equipment.sh status

# Show recent changes
./update_equipment.sh changes
```

### Method 3: Using API Endpoints
```bash
# Trigger sync via API
curl -X POST http://192.168.1.168:8001/api/equipment/sync

# Get equipment list via API
curl http://192.168.1.168:8001/api/equipment
```

## 📁 Folder Structure

Equipment photos should be organized as follows:
```
Equipment Photos/
├── Sequencing/
│   ├── DNBSEQ-G400.png
│   ├── DNBSEQ-G99.jpg
│   └── ...
├── Sample Prep/
│   ├── D4.jpg
│   ├── MGISP-100.png
│   └── ...
└── STOmics/
    ├── Leica DM6 Microscope.avif
    ├── Go Optical.webp
    └── ...
```

## 🔧 Equipment Management

### Adding New Equipment
1. **Add Photo**: Place image file in appropriate category folder
2. **Run Update**: Execute `./deploy.sh update` or `./deploy.sh sync`
3. **Verification**: Check equipment appears in booking interface

### Removing Equipment
1. **Remove Photo**: Delete image file from folder
2. **Run Update**: Execute `./deploy.sh update` or `./deploy.sh sync`
3. **Result**: Equipment marked as inactive, existing bookings preserved

### Updating Equipment Photos
1. **Replace Photo**: Keep same filename but update image content
2. **Run Update**: Execute update command
3. **Detection**: System detects file hash change and updates registry

## 📊 Equipment Registry Database

### Schema
```sql
CREATE TABLE equipment_registry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_id TEXT UNIQUE NOT NULL,
    equipment_name TEXT NOT NULL,
    category TEXT NOT NULL,
    image_filename TEXT NOT NULL,
    file_hash TEXT NOT NULL,
    folder_path TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    version TEXT DEFAULT ''
);
```

### Fields Explanation
- **equipment_id**: Safe ID used in URLs (lowercase, spaces → underscores)
- **equipment_name**: Display name from filename (without extension)
- **file_hash**: MD5 hash for detecting file changes
- **is_active**: Flag for active/inactive equipment
- **version**: Free-text firmware/software version string (e.g. `ECR2.5.1`); editable via the booking page UI or `PUT /api/equipment/<id>/version`

## 🔄 Automatic Detection

### What Gets Detected
- **File Addition**: New photos in any equipment folder
- **File Removal**: Missing photos marked as inactive
- **File Content Change**: Different file hash = photo updated
- **File Rename**: Treated as removal + addition
- **Format Change**: Different extension = new file

### What Does Not Get Detected
- **Folder Renames**: Requires manual database update
- **File Metadata Changes**: Only content hash matters
- **Temporary Files**: Files not matching image extensions ignored

## 📋 Change Reports

### Sample Output
```
Equipment registry updated successfully:
  +3 new equipment added
  -1 equipment removed
  ~2 photos updated
  Total changes: 6
```

### Detailed Logging
```
2026-01-30 10:12:33,880 - app - INFO - Added new equipment: DNBSEQ-G400 (sequencing)
2026-01-30 10:12:33,880 - app - INFO - Updated equipment photo: HistoCut Multicut Microtome
2026-01-30 10:12:33,880 - app - INFO - Marked equipment as inactive: Old_Equipment_ID
```

## 🛠️ Troubleshooting

### Equipment Not Appearing
```bash
# Check if photo is in correct folder
ls -la "Equipment Photos/Sequencing/"

# Check if file is valid image
file "Equipment Photos/Sequencing/photo.jpg"

# Run manual update with debug
./update_equipment.sh update
```

### Update Not Working
```bash
# Check database connection
python3 -c "from app import get_equipment_from_registry; print(len(get_equipment_from_registry()))"

# Check file permissions
ls -la "Equipment Photos/"

# Reinitialize registry if needed
rm bookings.db
./deploy.sh sync
```

### Large Number of Changes
If you see many unexpected changes:
1. Check if folder structure is correct
2. Verify image file formats are supported
3. Check for duplicate equipment names
4. Review logs for error messages

## 📈 Performance Considerations

### Optimization Features
- **Lazy Loading**: Registry only when needed
- **Fallback Support**: Uses filesystem scan if registry empty
- **Efficient Hashing**: MD5 calculation for change detection
- **Batch Operations**: Single database transaction for all changes

### Best Practices
- **Regular Updates**: Run sync after photo changes
- **Batch Changes**: Make multiple photo changes before single sync
- **Monitor Logs**: Watch for unexpected equipment changes
- **Backup Database**: Keep registry backups before major changes

## 🔗 Integration with Booking System

### Real-time Updates
- Equipment registry used as primary data source
- Fallback to filesystem scanning for robustness
- Existing bookings preserved when equipment removed
- Updated photos reflected immediately in booking interface

### API Integration
- REST endpoints for external integration
- JSON responses with equipment details
- Status endpoints for monitoring
- Sync endpoints for automated updates

---

The equipment photo update system ensures your booking system always stays synchronized with your equipment photo library, making equipment management effortless and reliable.