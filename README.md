# alx-backend-graphql_crm
This project implements a CRM (Customer Relationship Management) system using GraphQL with Django and Graphene-Django.
It demonstrates how to build flexible APIs that let clients query exactly what they need — unlike REST, which returns fixed responses.

Learning Objectives

By completing this project, I learned how to:

Explain what GraphQL is and how it differs from REST.

Build and expose a GraphQL schema with Queries and Mutations.

Integrate Django models with GraphQL using graphene-django.

Implement mutations to create customers, products, and orders.

Use filters and pagination to query data efficiently.

Seed and test data through GraphiQL or API tools.

 Project Structure
alx-backend-graphql/
│
├── alx_backend_graphql/        # Main Django project
│   ├── settings.py             # Django + Graphene configuration
│   ├── schema.py               # Root GraphQL schema (hello + mutations)
│   └── urls.py                 # Routes GraphQL endpoint
│
├── crm/                        # Main app for CRM logic
│   ├── models.py               # Customer, Product, Order models
│   ├── schema.py               # GraphQL types, queries, mutations
│   ├── filters.py              # Filtering logic with django-filters
│   └── migrations/             # Database migrations
│
├── seed_db.py                  # Seeds database with sample data
├── db.sqlite3                  # SQLite database
└── README.md                   # Project documentation

 Core Concepts Implemented
1. GraphQL Endpoint

A single endpoint /graphql is set up in urls.py using:

path("graphql", csrf_exempt(GraphQLView.as_view(graphiql=True))),


Test query:

{
  hello
}


Response:

{
  "data": { "hello": "Hello, GraphQL!" }
}

2. Models

Customer → name, email, phone

Product → name, price, stock

Order → customer, products, total_amount, order_date

Each model is connected to the database using Django ORM.

3. Mutations

Implemented in crm/schema.py:

CreateCustomer → Add a single customer.

BulkCreateCustomers → Add multiple customers with validation and partial success.

CreateProduct → Add products with numeric validation.

CreateOrder → Create orders linked to customers and products with calculated totals.

Example mutation:

mutation {
  createCustomer(input: {
    name: "Alice",
    email: "alice@example.com",
    phone: "+1234567890"
  }) {
    customer { id name email }
    message
  }
}

4. Filtering

Implemented in crm/filters.py using django-filters.
Supports filtering by:

Customer name, email, phone, creation date

Product name, price range, stock

Order amount, date, customer, or product name

Example:

query {
  allProducts(filter: { priceGte: 100, priceLte: 1000 }, orderBy: "-stock") {
    id
    name
    price
    stock
  }
}

5. Seeding

Run:

python3 seed_db.py


This adds sample customers, products, and orders for testing.

 Setup & Usage
1. Clone the repo with ssh:
git@github.com:garisonmike/alx-backend-graphql_crm.git 
or for https:
https://github.com/garisonmike/alx-backend-graphql_crm.git
cd alx-backend-graphql

2. Install dependencies
pip install -r requirements.txt

3. Apply migrations
python3 manage.py migrate

4. Run server
python3 manage.py runserver


Visit  http://localhost:8000/graphql

 Tasks Summary
Task	Description	Status
0	Setup GraphQL endpoint with hello query	 Passed
1	Build CRM database & GraphQL mutations	 Passed
2	Implement complex nested mutations	 Passed
3	Add filtering for queries	 Passed
 Notes

Project name must be alx_backend_graphql (not _crm) for ALX checker to pass.

GraphQL endpoint: /graphql

Uses SQLite for simplicity; can be swapped for MySQL/PostgreSQL easily.