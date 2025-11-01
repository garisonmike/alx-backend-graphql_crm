import os
from datetime import datetime
from decimal import Decimal
from celery import shared_task
from django.db.models import Sum, Count
from .models import Customer, Order, Product


@shared_task
def generate_crm_report():
    """
    Generate a weekly CRM report summarizing:
    - Total number of customers
    - Total number of orders  
    - Total revenue (sum of all order amounts)
    
    Logs the report to /tmp/crm_report_log.txt with timestamp.
    """
    try:
        # Fetch CRM statistics using Django ORM
        total_customers = Customer.objects.count()
        total_orders = Order.objects.count()
        
        # Calculate total revenue from all orders
        revenue_result = Order.objects.aggregate(total_revenue=Sum('total_amount'))
        total_revenue = revenue_result['total_revenue'] or Decimal('0.00')
        
        # Format the report message
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report_message = (
            f"{timestamp} - Report: {total_customers} customers, "
            f"{total_orders} orders, {total_revenue} revenue"
        )
        
        # Write report to log file
        log_file = '/tmp/crm_report_log.txt'
        with open(log_file, 'a') as f:
            f.write(f"{report_message}\n")
        
        # Return summary for Celery logs
        return f"CRM report generated: {total_customers} customers, {total_orders} orders, ${total_revenue} revenue"
        
    except Exception as e:
        # Log errors for debugging
        error_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_message = f"{error_timestamp} - Error generating report: {str(e)}\n"
        
        with open('/tmp/crm_report_log.txt', 'a') as f:
            f.write(error_message)
        
        raise
