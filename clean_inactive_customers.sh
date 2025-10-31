#!/bin/bash
# ----------------------------------------------------------------------
# Script Name: clean_inactive_customers.sh
# Description: Deletes customers who have not placed any orders
#              within the last 12 months. Logs the total deleted count
#              to /tmp/customer_cleanup_log.txt with a timestamp.
# ----------------------------------------------------------------------

# Define project and Python paths
PROJECT_DIR="/home/spiderman/Projects/alx-backend-graphql_crm"
PYTHON_BIN="$PROJECT_DIR/venv/bin/python"

# Navigate to the project directory
cd "$PROJECT_DIR" || exit 1

# Run Django shell command to delete inactive customers
DELETED_COUNT=$($PYTHON_BIN manage.py shell -c "
from datetime import timedelta
from django.utils import timezone
from crm.models import Customer
cutoff = timezone.now() - timedelta(days=365)
deleted, _ = Customer.objects.filter(orders__isnull=True, date_joined__lt=cutoff).delete()
print(deleted)
")

# Log the result with timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo \"$TIMESTAMP - Deleted $DELETED_COUNT inactive customers\" >> /tmp/customer_cleanup_log.txt
