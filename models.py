from config import db
import requests
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class SoldProduct(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='sold_products')
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    sold_at = db.Column(db.DateTime, default=datetime.utcnow)
    quantity = db.Column(db.Integer, nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(200), nullable=True)
    category = db.Column(db.String(100), nullable=True)

def get_products_from_api():
    try:
        response = requests.get('https://fakestoreapi.com/products')
        if response.status_code == 200:
            return response.json()
        return []
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return []

def insert_products_into_db():
    products = get_products_from_api()
    for product in products:
        # Check if the product already exists in the database
        existing_product = Product.query.filter_by(id=product['id']).first()
        if not existing_product:
            # Create a new product entry if it doesn't exist
            new_product = Product(
                id=product['id'],
                title=product['title'],
                description=product['description'],
                price=product['price'],
                image=product['image'],
                category=product.get('category', 'Uncategorized')
            )
            db.session.add(new_product)
    db.session.commit()

