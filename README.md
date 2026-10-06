# Mini E-Commerce API

A small e-commerce backend built using **FastAPI, SQLite, SQLAlchemy and Pydantic**.

The application allows users to create products, place orders, retrieve orders and update order status.

## Technologies

* Python
* FastAPI
* SQLite
* SQLAlchemy
* Pydantic
* Uvicorn

## Project Structure

```text
ecommerce_api/
│
├── main.py
├── database.py
├── models.py
├── schemas.py
├── exceptions.py
├── requirements.txt
├── README.md
└── ecommerce.db
```

## Installation

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the Application

```bash
uvicorn main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## APIs

### Create Product

```text
POST /products
```

Example request:

```json
{
    "name": "Laptop",
    "price": 55000,
    "stock": 10
}
```

### Get Products

```text
GET /products
```

### Place Order

```text
POST /orders
```

Example:

```json
{
    "customer": "Avro",
    "items": [
        {
            "product_id": 1,
            "quantity": 2
        }
    ]
}
```

The client does **not** provide the total amount.

The server calculates:

```text
Product price × quantity
```

For example:

```text
Laptop = ₹55,000
Quantity = 2

Total = ₹55,000 × 2
      = ₹110,000
```

The initial order status is automatically:

```text
PLACED
```

### Get All Orders

```text
GET /orders
```

### Get Specific Order

```text
GET /orders/{order_id}
```

Example:

```text
GET /orders/1
```

### Update Order Status

```text
PUT /orders/{order_id}/status
```

Example:

```json
{
    "status": "PROCESSING"
}
```

Valid order flow:

```text
PLACED
   ↓
PROCESSING
   ↓
SHIPPED
   ↓
DELIVERED
```

Invalid transitions are rejected.

For example:

```text
PLACED → SHIPPED
```

will return an error.

## Validation

The API validates:

* Product name must contain at least 2 characters.
* Product price must be greater than 0.
* Product stock cannot be negative.
* Product ID must exist when placing an order.
* Order quantity must be greater than 0.
* Requested quantity cannot exceed available stock.
* Order total is calculated by the server.
* Only valid order status values are accepted.
* Order status must follow the defined sequence.

## Important Design Decision

The client cannot manipulate the order total.

The client sends:

```json
{
    "customer": "Avro",
    "items": [
        {
            "product_id": 1,
            "quantity": 2
        }
    ]
}
```

The backend retrieves the actual product price from the database and calculates:

```python
total_amount += product.price * item.quantity
```

This prevents a client from submitting an incorrect amount such as:

```json
{
    "total_amount": 1
}
```

## Database

SQLite is used for simplicity.

The database file:

```text
ecommerce.db
```

is automatically created when the application starts.

The application contains three tables:

```text
products
orders
order_items
```

`order_items` connects products with orders and stores the quantity and price at the time the order was placed.

## Example Workflow

### Step 1 — Create Product

```http
POST /products
```

```json
{
    "name": "Laptop",
    "price": 55000,
    "stock": 5
}
```

### Step 2 — Create Another Product

```json
{
    "name": "Mouse",
    "price": 1500,
    "stock": 20
}
```

### Step 3 — Place Order

```http
POST /orders
```

```json
{
    "customer": "Avro",
    "items": [
        {
            "product_id": 1,
            "quantity": 1
        },
        {
            "product_id": 2,
            "quantity": 2
        }
    ]
}
```

The server calculates:

```text
Laptop = 55,000 × 1 = 55,000
Mouse  =  1,500 × 2 =  3,000

Total = 58,000
```

### Step 4 — Process Order

```http
PUT /orders/1/status
```

```json
{
    "status": "PROCESSING"
}
```

### Step 5 — Ship Order

```json
{
    "status": "SHIPPED"
}
```

### Step 6 — Deliver Order

```json
{
    "status": "DELIVERED"
}
```

## Learning Concepts

This project demonstrates:

* FastAPI routing
* REST APIs
* CRUD operations
* SQLite
* SQLAlchemy ORM
* Database relationships
* Pydantic validation
* Request and response schemas
* HTTP status codes
* Dependency injection
* Server-side business logic
* Inventory management
* Order state management
* Exception handling
* One-to-many relationships
* API documentation with Swagger
