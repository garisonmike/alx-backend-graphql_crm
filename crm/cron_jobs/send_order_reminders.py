#!/usr/bin/env python3
"""
send_order_reminders.py

This script queries the GraphQL endpoint to find orders placed within the
last 7 days and logs reminders for each order.

Author: ALX Backend Developer
"""

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime, timedelta

# GraphQL endpoint
GRAPHQL_URL = "http://localhost:8000/graphql"

# Calculate the date range (last 7 days)
today = datetime.now().date()
seven_days_ago = today - timedelta(days=7)

# Define the GraphQL query
query = gql("""
query RecentOrders($startDate: Date!) {
  allOrders(orderDate_Gte: $startDate) {
    edges {
      node {
        id
        customer {
          email
        }
      }
    }
  }
}
""")

# Define variables for the query
variables = {"startDate": str(seven_days_ago)}

try:
    # Setup transport and client
    transport = RequestsHTTPTransport(url=GRAPHQL_URL)
    client = Client(transport=transport, fetch_schema_from_transport=False)
    
    # Execute the query
    result = client.execute(query, variable_values=variables)
    
    # Extract order data
    orders = result.get("allOrders", {}).get("edges", [])

    # Open the log file
    with open("/tmp/order_reminders_log.txt", "a") as log_file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if orders:
            for edge in orders:
                order = edge.get("node", {})
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
