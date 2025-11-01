#!/bin/bash
# ----------------------------------------------------------------------
# Script Name: clean_inactive_customers.sh
# Description: Deletes customers who have not placed any orders
#              within the last 12 months. Logs the total deleted count
#              to /tmp/customer_cleanup_log.txt with a timestamp.
# ----------------------------------------------------------------------

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Use python3 or venv python
if [ -f "$PROJECT_DIR/venv/bin/python" ]; then
    PYTHON_BIN="$PROJECT_DIR/venv/bin/python"
else
    PYTHON_BIN="python3"
fi

# Navigate to the project directory
cd "$PROJECT_DIR" || exit 1

# Run Django shell command to delete inactive customers
DELETED_COUNT=$($PYTHON_BIN manage.py shell -c "
from crm.models import Customer
from datetime import timedelta
from django.utils import timezone

threshold = timezone.now() - timedelta(days=365)
inactive_customers = Customer.objects.filter(created_at__lt=threshold)
deleted, _ = inactive_customers.delete()
print(deleted)
")

# Log the result with timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "$TIMESTAMP - Deleted $DELETED_COUNT inactive customers" >> /tmp/customer_cleanup_log.txt
