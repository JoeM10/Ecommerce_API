from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Table, String, Column, select, DateTime
from marshmallow import ValidationError, fields, validate
from typing import List, Optional
from datetime import datetime
import os

# ====================
# Initial Setup
# ====================

mySQL_Password = os.getenv("MYSQL_PASS")

# Initialize Flask app
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+mysqlconnector://root:{mySQL_Password}@localhost/ecommerce_api"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create Base Class
class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
db.init_app(app)
ma = Marshmallow(app)

# ====================
# Models
# ====================

# Association table for Order <-> Product many-to-many
order_product = Table(
    "order_product",
    Base.metadata,
    Column("order_id", ForeignKey("orders.id"), primary_key=True),
    Column("product_id", ForeignKey("products.id"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    address: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(200), unique=True)

    # Relationships
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="user")

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="orders")
    products: Mapped[List["Product"]] = relationship("Product", secondary=order_product, back_populates="orders")

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column(String(100))
    price: Mapped[float] = mapped_column()

    # Relationships
    orders: Mapped[List["Order"]] = relationship("Order", secondary=order_product, back_populates="products")

# ====================
# Schemas
# ====================

class UserSchema(ma.SQLAlchemyAutoSchema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=50))
    address = fields.String(required=True, validate=validate.Length(min=1, max=200))
    email = fields.Email(required=True, validate=validate.Length(min=1, max=200))

    class Meta:
        model = User
        dump_only = ["id", "orders"]
        include_relationships = True
        include_fk = True

class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order
        load_only = ["user_id"]
        dump_only = ["id", "user", "products"]
        include_relationships = True
        include_fk = True

class ProductSchema(ma.SQLAlchemyAutoSchema):
    product_name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    price = fields.Float(required=True, validate=validate.Range(min=0))

    class Meta:
        model = Product
        dump_only = ["id", "orders"]
        include_relationships = True
        include_fk = True

user_schema = UserSchema()
users_schema = UserSchema(many=True)

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

# ====================
# Routes
# ====================

# ========== User Routes ========== #

# GET a user
@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    return user_schema.jsonify(user), 200

# GET all users
@app.route("/users", methods=["GET"])
def get_users():
    users = db.session.execute(select(User)).scalars().all()
    return users_schema.jsonify(users), 200

# POST a new user
@app.route("/users", methods=["POST"])
def create_user():
    try:
        user_data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_user = User(name=user_data["name"], address=user_data["address"], email=user_data["email"])
    db.session.add(new_user)
    db.session.commit()

    return user_schema.jsonify(new_user), 201

# PUT a user
@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    try:
        user_data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    user.name = user_data["name"]
    user.address = user_data["address"]
    user.email = user_data["email"]

    db.session.commit()
    return user_schema.jsonify(user), 200

# DELETE a user
@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"}), 200


# ========== Product Routes ========== #

# GET a product
@app.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"message": "Product not found"}), 404
    return product_schema.jsonify(product), 200

# GET all products
@app.route("/products", methods=["GET"])
def get_products():
    products = db.session.execute(select(Product)).scalars().all()
    return products_schema.jsonify(products), 200

# POST a new product
@app.route("/products", methods=["POST"])
def create_product():
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_product = Product(product_name=product_data["product_name"], price=product_data["price"])
    db.session.add(new_product)
    db.session.commit()

    return product_schema.jsonify(new_product), 201

# PUT a product
@app.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"message": "Product not found"}), 404

    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    product.product_name = product_data["product_name"]
    product.price = product_data["price"]

    db.session.commit()
    return product_schema.jsonify(product), 200

# DELETE a product
@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"message": "Product not found"}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted successfully"}), 200


# ========== Order Routes ========== #

# GET all orders from all users
@app.route("/orders", methods=["GET"])
def get_orders():
    orders = db.session.execute(select(Order)).scalars().all()
    return orders_schema.jsonify(orders), 200

# GET all orders for a user via user id
@app.route("/orders/user/<int:user_id>", methods=["GET"])
def get_orders_by_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    orders = user.orders
    return orders_schema.jsonify(orders), 200

# GET all products in an order via order id
@app.route("/orders/<int:order_id>/products", methods=["GET"])
def get_products_in_order(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({"message": "Order not found"}), 404

    return products_schema.jsonify(order.products), 200

# POST a new order for a user
@app.route("/orders", methods=["POST"])
def create_order():
    user_id = request.json.get("user_id")
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    try:
        product_ids = request.json.get("product_ids", [])
        products = db.session.execute(select(Product).where(Product.id.in_(product_ids))).scalars().all()
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_order = Order(user_id=user_id)
    new_order.products.extend(products)
    db.session.add(new_order)
    db.session.commit()

    return order_schema.jsonify(new_order), 201

# PUT an order to add a single product to it
@app.route("/orders/<int:order_id>/add_product/<int:product_id>", methods=["PUT"])
def add_products_to_order(order_id, product_id):
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({"message": "Order not found"}), 404

    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"message": "Product not found"}), 404

    if product in order.products:
        return jsonify({"message": "Product already in order"}), 400

    order.products.append(product)
    db.session.commit()

    return order_schema.jsonify(order), 200

# PUT an order to add multiple products to it
@app.route("/orders/<int:order_id>/add_products", methods=["PUT"])
def add_multiple_products_to_order(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({"message": "Order not found"}), 404

    product_ids = request.json.get("product_ids", [])
    products = db.session.execute(select(Product).where(Product.id.in_(product_ids))).scalars().all()

    for product in products:
        if product not in order.products:
            order.products.append(product)

    db.session.commit()
    return order_schema.jsonify(order), 200

# PUT an order to remove a single product from it
@app.route("/orders/<int:order_id>/remove_product/<int:product_id>", methods=["PUT"])
def remove_product_from_order(order_id, product_id):
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({"message": "Order not found"}), 404

    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"message": "Product not found"}), 404

    if product not in order.products:
        return jsonify({"message": "Product not in order"}), 404

    order.products.remove(product)
    db.session.commit()

    return order_schema.jsonify(order), 200

# PUT an order to remove multiple products from it
@app.route("/orders/<int:order_id>/remove_products", methods=["PUT"])
def remove_multiple_products_from_order(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({"message": "Order not found"}), 404

    product_ids = request.json.get("product_ids", [])
    products = db.session.execute(select(Product).where(Product.id.in_(product_ids))).scalars().all()

    for product in products:
        if product in order.products:
            order.products.remove(product)

    db.session.commit()
    return order_schema.jsonify(order), 200

# DELETE an order
@app.route("/orders/<int:order_id>", methods=["DELETE"])
def delete_order(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({"message": "Order not found"}), 404

    db.session.delete(order)
    db.session.commit()
    return jsonify({"message": "Order deleted successfully"}), 200


# ====================
# Runs db and app
# ====================

if __name__ == "__main__":

    with app.app_context():
        # db.drop_all() # Uncomment this line to drop all tables and start fresh
        db.create_all()

    app.run(debug=True)