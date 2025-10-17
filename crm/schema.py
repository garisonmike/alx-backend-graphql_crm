import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from .models import Customer, Product, Order
from django.core.exceptions import ValidationError
from django.db import transaction
from datetime import datetime
from decimal import Decimal
from .filters import CustomerFilter, ProductFilter, OrderFilter


# ---------- GraphQL Types ----------
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = "__all__"
        interfaces = (graphene.relay.Node,)  # needed for filter connections


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__"
        interfaces = (graphene.relay.Node,)


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = "__all__"
        interfaces = (graphene.relay.Node,)


# ---------- Queries ----------
class Query(graphene.ObjectType):
    # add filtering support using django-filter
    all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter)
    all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter)
    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter)


# ---------- Mutations ----------
class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=False)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, name, email, phone=None):
        if Customer.objects.filter(email=email).exists():
            raise ValidationError("Email already exists")
        customer = Customer(name=name, email=email, phone=phone)
        customer.save()
        return CreateCustomer(customer=customer, message="Customer created successfully")


class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String(required=False)


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        # ALX expects the argument name to be `input` (list of customers)
        input = graphene.List(CustomerInput, required=True)

    # ALX expects the payload field to be `customers`, along with `errors`
    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)
    message = graphene.String()

    @classmethod
    @transaction.atomic
    def mutate(cls, root, info, input):
        created, errors = [], []
        for cust in input:
            try:
                if Customer.objects.filter(email=cust.email).exists():
                    raise ValidationError(f"Email {cust.email} already exists")
                obj = Customer(name=cust.name, email=cust.email, phone=cust.phone)
                obj.full_clean()
                obj.save()
                created.append(obj)
            except Exception as e:
                errors.append(str(e))
        msg = (
            "Bulk create completed with partial success" if errors else "Bulk create successful"
        )
        return BulkCreateCustomers(customers=created, errors=errors, message=msg)


class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.String(required=True)
        stock = graphene.Int(required=False)

    product = graphene.Field(ProductType)

    def mutate(self, info, name, price, stock=0):
        try:
            price_decimal = Decimal(price)
        except Exception:
            raise ValidationError("Invalid price format. Use a numeric string like '999.99'.")

        if price_decimal <= 0:
            raise ValidationError("Price must be positive")
        if stock < 0:
            raise ValidationError("Stock cannot be negative")

        product = Product(name=name, price=price_decimal, stock=stock)
        product.save()
        return CreateProduct(product=product)


class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)
        order_date = graphene.DateTime(required=False)

    order = graphene.Field(OrderType)

    def mutate(self, info, customer_id, product_ids, order_date=None):
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            raise ValidationError("Invalid customer ID")

        products = list(Product.objects.filter(pk__in=product_ids))
        if not products:
            raise ValidationError("Invalid product IDs")

        order = Order(customer=customer, order_date=order_date or datetime.now())
        order.save()
        order.products.set(products)
        order.total_amount = sum(p.price for p in products)
        order.save()
        return CreateOrder(order=order)


# ---------- Root Mutation ----------
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
