import datetime
import os
import requests

def log_crm_heartbeat():
    """
    Logs a heartbeat message every 5 minutes to confirm the CRM system is active.
    Optionally checks the GraphQL endpoint for responsiveness.
    """
    log_file = '/tmp/crm_heartbeat_log.txt'
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")

    # Write heartbeat message
    with open(log_file, 'a') as f:
        f.write(f"{timestamp} CRM is alive\n")

    # Optional: test GraphQL hello query for endpoint health
    try:
        response = requests.post(
            'http://localhost:8000/graphql/',
            json={'query': '{ hello }'}
        )
        if response.status_code == 200:
            with open(log_file, 'a') as f:
                f.write(f"{timestamp} GraphQL endpoint responsive\n")
        else:
            with open(log_file, 'a') as f:
                f.write(f"{timestamp} GraphQL endpoint error: {response.status_code}\n")
    except Exception as e:
        with open(log_file, 'a') as f:
            f.write(f"{timestamp} Error checking GraphQL endpoint: {e}\n")


def update_low_stock():
    """
    Executes the UpdateLowStockProducts mutation to restock products with stock < 10.
    Logs the updated products and their new stock levels.
    """
    log_file = '/tmp/low_stock_updates_log.txt'
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    mutation = """
    mutation {
        updateLowStockProducts {
            products {
                id
                name
                stock
            }
            message
        }
    }
    """
    
    try:
        response = requests.post(
            'http://localhost:8000/graphql/',
            json={'query': mutation}
        )
        
        if response.status_code == 200:
            data = response.json()
            result = data.get('data', {}).get('updateLowStockProducts', {})
            products = result.get('products', [])
            message = result.get('message', '')
            
            with open(log_file, 'a') as f:
                f.write(f"[{timestamp}] {message}\n")
                for product in products:
                    f.write(f"[{timestamp}] Updated Product: {product['name']}, New Stock: {product['stock']}\n")
        else:
            with open(log_file, 'a') as f:
                f.write(f"[{timestamp}] Error: HTTP {response.status_code}\n")
    except Exception as e:
        with open(log_file, 'a') as f:
            f.write(f"[{timestamp}] Error updating low stock: {e}\n")
