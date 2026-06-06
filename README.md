# E-Commerce API with Flask

A RESTful E-Commerce API built with Flask, SQLAlchemy, MySQL, and Marshmallow. This project manages users, products, and orders while demonstrating one-to-many and many-to-many database relationships.

## Features

* User CRUD operations
* Product CRUD operations
* Order creation and management
* Add and remove products from orders
* One user can have many orders
* Many orders can contain many products
* Marshmallow validation and serialization
* MySQL database integration
* Postman collection for API testing

## Technologies Used

* Python
* Flask
* Flask-SQLAlchemy
* Flask-Marshmallow
* Marshmallow-SQLAlchemy
* MySQL
* MySQL Connector
* Postman
* MySQL Workbench

## Database Models

### User

* `id`
* `name`
* `address`
* `email` — unique

### Order

* `id`
* `order_date`
* `user_id` — foreign key to `users.id`

### Product

* `id`
* `product_name`
* `price`

### Order_Product

Association table used for the many-to-many relationship between orders and products.

* `order_id` — foreign key to `orders.id`
* `product_id` — foreign key to `products.id`

The combined `order_id` and `product_id` primary keys help prevent duplicate products from being added to the same order.

## Setup Instructions

### 1. Create and activate a virtual environment

```bash
python3 -m venv venv
```

Mac/Linux:

```bash
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install Flask Flask-SQLAlchemy Flask-Marshmallow marshmallow-sqlalchemy mysql-connector-python
```

### 3. Create the MySQL database

In MySQL Workbench, create a database named:

```sql
CREATE DATABASE ecommerce_api;
```

### 4. Set the MySQL password environment variable

Mac/Linux:

```bash
export MYSQL_PASS="your_mysql_password"
```

Windows PowerShell:

```powershell
$env:MYSQL_PASS="your_mysql_password"
```

Windows Command Prompt:

```cmd
set MYSQL_PASS=your_mysql_password
```

### 5. Run the app

```bash
python E_Commerce_API_with_Flask.py
```

The app runs at:

```text
http://127.0.0.1:5000
```

## API Endpoints

### Users

| Method | Endpoint           | Description   |
| ------ | ------------------ | ------------- |
| GET    | `/users`           | Get all users |
| GET    | `/users/<user_id>` | Get one user  |
| POST   | `/users`           | Create a user |
| PUT    | `/users/<user_id>` | Update a user |
| DELETE | `/users/<user_id>` | Delete a user |

Example user JSON:

```json
{
  "name": "Joe McDaniel",
  "address": "123 Example Street",
  "email": "joe@example.com"
}
```

### Products

| Method | Endpoint                 | Description      |
| ------ | ------------------------ | ---------------- |
| GET    | `/products`              | Get all products |
| GET    | `/products/<product_id>` | Get one product  |
| POST   | `/products`              | Create a product |
| PUT    | `/products/<product_id>` | Update a product |
| DELETE | `/products/<product_id>` | Delete a product |

Example product JSON:

```json
{
  "product_name": "Keyboard",
  "price": 79.99
}
```

### Orders

| Method | Endpoint                                         | Description                         |
| ------ | ------------------------------------------------ | ----------------------------------- |
| GET    | `/orders`                                        | Get all orders                      |
| GET    | `/orders/user/<user_id>`                         | Get all orders for a user           |
| GET    | `/orders/<order_id>/products`                    | Get all products in an order        |
| POST   | `/orders`                                        | Create an order                     |
| PUT    | `/orders/<order_id>/add_product/<product_id>`    | Add product to order                |
| PUT    | `/orders/<order_id>/add_products`                | Add multiple products to order      |
| DELETE | `/orders/<order_id>/remove_product/<product_id>` | Remove product from order           |
| DELETE | `/orders/<order_id>/remove_products`             | Remove multiple products from order |
| DELETE | `/orders/<order_id>`                             | Delete an order                     |

Example order JSON:

```json
{
  "user_id": 1,
  "product_ids": [1, 2]
}
```

## Validation

Marshmallow is used to validate and serialize data.

Validation includes:

* Required user name
* Required user address
* Valid email address
* Required product name
* Product price must be greater than or equal to 0

## Testing

Use the Postman collection to test each endpoint.
There is a test request for each endpoint in the collection.

Use MySQL Workbench to verify the data:

```sql
USE ecommerce_api;
SHOW TABLES;
SELECT * FROM users;
SELECT * FROM products;
SELECT * FROM orders;
SELECT * FROM order_product;
```

## Author

Created by Joseph McDaniel
Github: https://github.com/JoeM10/