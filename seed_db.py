#!/usr/bin/env python3
import os
import django
from decimal import Decimal
from datetime import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_backend_graphql_crm.settings")
django.setup()

from crm.models import Customer, Product, Order


def seed_customers():
    customers = [
        {"name": "Alice", "email": "alice@example.com", "phone": "+1234567890"},
        {"name": "Bob", "email": "bob@example.com", "phone": "123-456-7890"},
        {"name": "Carol", "email": "carol@example.com", "phone": None},
    ]
    for data in customers:
        Customer.objects.get_or_create(email=data["email"], defaults=data)
    print("Seeded customers successfully.")


def seed_products():
    products = [
        {"name": "Laptop", "price": Decimal("999.99"), "stock": 10},
        {"name": "Phone", "price": Decimal("499.99"), "stock": 25},
        {"name": "Headphones", "price": Decimal("199.99"), "stock": 15},
    ]
    for data in products:
        Product.objects.get_or_create(name=data["name"], defaults=data)
    print("Seeded products successfully.")


def seed_orders():
    customer = Customer.objects.first()
    if not customer:
        print("No customers found. Seed customers first.")
        return

    products = list(Product.objects.all()[:2])
    if not products:
        print("No products found. Seed products first.")
        return

    order, created = Order.objects.get_or_create(
        customer=customer,
        defaults={"order_date": datetime.now(), "total_amount": sum(p.price for p in products)},
    )
    order.products.set(products)
    order.save()
    print("Seeded orders successfully.")


def run():
    seed_customers()
    seed_products()
    seed_orders()


if __name__ == "__main__":
    run()
