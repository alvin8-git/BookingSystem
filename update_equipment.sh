#!/bin/bash

# Equipment Photo Update Script
# Standalone script to update equipment registry when photos change

set -e

# Configuration
APP_DIR="/data/alvin/BookingSystem"
LOG_FILE="$APP_DIR/logs/equipment_update.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create logs directory if it doesn't exist
mkdir -p "$(dirname "$LOG_FILE")"

echo -e "${GREEN}Equipment Photo Update Script${NC}"
echo "=================================="

# Function to log messages
log_message() {
    local level=$1
    local message=$2
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message" | tee -a "$LOG_FILE"
}

# Function to update equipment registry
update_equipment() {
    log_message "INFO" "Starting equipment registry update"
    
    # Change to application directory
    cd "$APP_DIR"
    
    # Run equipment sync
    python3 -c "
import sys
sys.path.append('.')
from app import init_db, sync_equipment_registry
try:
    init_db()
    result = sync_equipment_registry()
    if 'error' in result:
        print(f'Error: {result[\"error\"]}')
        sys.exit(1)
    else:
        changes = result['total']
        if changes > 0:
            print(f'Equipment registry updated successfully:')
            print(f'  +{result[\"added\"]} new equipment added')
            print(f'  -{result[\"removed\"]} equipment removed')
            print(f'  ~{result[\"updated\"]} photos updated')
            print(f'  Total changes: {changes}')
        else:
            print('No equipment changes detected')
except Exception as e:
    print(f'Exception occurred: {e}')
    sys.exit(1)
" 2>&1 | tee -a "$LOG_FILE"
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        log_message "SUCCESS" "Equipment registry update completed successfully"
        echo -e "${GREEN}Equipment update completed successfully${NC}"
    else
        log_message "ERROR" "Equipment registry update failed"
        echo -e "${RED}Equipment update failed. Check log file: $LOG_FILE${NC}"
    fi
    
    return $exit_code
}

# Function to show equipment registry status
show_status() {
    echo -e "${GREEN}Current Equipment Registry Status${NC}"
    echo "==================================="
    
    cd "$APP_DIR"
    
    python3 -c "
import sys
sys.path.append('.')
from app import get_equipment_from_registry, CATEGORIES

try:
    equipment = get_equipment_from_registry(active_only=True)
    
    print(f'Total active equipment: {len(equipment)}')
    print()
    
    # Group by category
    by_category = {}
    for cat_key in CATEGORIES.keys():
        by_category[cat_key] = []
    
    for eq in equipment:
        category = eq['category']
        if category in by_category:
            by_category[category].append(eq)
    
    for cat_key, cat_data in CATEGORIES.items():
        cat_equipment = by_category.get(cat_key, [])
        print(f'{cat_data[\"name\"]} ({cat_data[\"folder\"]}): {len(cat_equipment)} equipment')
        for eq in sorted(cat_equipment, key=lambda x: x['equipment_name']):
            print(f'  • {eq[\"equipment_name\"]} ({eq[\"image_filename\"]})')
        print()
        
except Exception as e:
    print(f'Error getting equipment status: {e}')
    sys.exit(1)
"
}

# Function to show recent equipment changes
show_changes() {
    echo -e "${GREEN}Recent Equipment Changes${NC}"
    echo "=========================="
    
    cd "$APP_DIR"
    
    python3 -c "
import sys
sys.path.append('.')
from app import get_equipment_from_registry

try:
    # Get all equipment (including inactive) to show changes
    equipment = get_equipment_from_registry(active_only=False)
    
    # Sort by updated_at descending
    equipment.sort(key=lambda x: x['updated_at'], reverse=True)
    
    print('Recent equipment modifications:')
    for eq in equipment[:10]:  # Show last 10 changes
        status = '✅ Active' if eq['is_active'] else '❌ Inactive'
        print(f'  {eq[\"updated_at\"]} {status} {eq[\"equipment_name\"]} ({eq[\"category\"]})')
        
except Exception as e:
    print(f'Error getting equipment changes: {e}')
    sys.exit(1)
"
}

# Main script logic
case "${1:-update}" in
    update)
        update_equipment
        ;;
    status)
        show_status
        ;;
    changes)
        show_changes
        ;;
    *)
        echo "Usage: $0 {update|status|changes}"
        echo "  update  - Update equipment registry with photo changes"
        echo "  status  - Show current equipment registry status"
        echo "  changes - Show recent equipment changes"
        echo ""
        echo "Examples:"
        echo "  $0 update      # Sync equipment after adding/removing photos"
        echo "  $0 status      # View current equipment in registry"
        echo "  $0 changes     # Show recent modifications"
        exit 1
        ;;
esac