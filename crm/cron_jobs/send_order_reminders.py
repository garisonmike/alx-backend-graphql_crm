#!/usr/bin/env python3
"""
send_order_reminders.py

This script queries the GraphQL endpoint to find orders placed within the
last 7 days and logs reminders for each order.

Author: ALX Backend Developer
"""

import requests
from datetime import datetime, timedelta

# GraphQL endpoint
GRAPHQL_URL = "http://localhost:8000/graphql"

# Calculate the date range (last 7 days)
today = datetime.now().date()
seven_days_ago = today - timedelta(days=7)

# Define the GraphQL query
query = """
query RecentOrders($startDate: Date!) {
  allOrders(orderDate_Gte: $startDate) {
    id
    customer {
      email
    }
  }
}
"""

# Define variables for the query
variables = {"startDate": str(seven_days_ago)}

try:
    # Send request to the GraphQL API
    response = requests.post(GRAPHQL_URL, json={"query": query, "variables": variables})
    data = response.json()

    # Extract order data
    orders = data.get("data", {}).get("allOrders", [])

    # Open the log file
    with open("/tmp/order_reminders_log.txt", "a") as log_file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if orders:
            for order in orders:
                order_id = order.get("id")
                customer_email = order.get("customer", {}).get("email", "N/A")
                log_file.write(f"[{timestamp}] Reminder: Order ID {order_id}, Customer: {customer_email}\n")
        else:
            log_file.write(f"[{timestamp}] No pending orders found in the last 7 days.\n")

    print("Order reminders processed!")

except Exception as e:
    with open("/tmp/order_reminders_log.txt", "a") as log_file:
        log_file.write(f"[{datetime.now()}] Error processing reminders: {e}\n")
    print("An error occurred while processing order reminders.")
