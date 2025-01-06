import requests
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from form import RegistrationForm, LoginForm

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True  # Enable SQL logging for debugging
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class SoldProduct(db.Model):
    __tablename__ = 'sold_product'  # Explicit table name for clarity
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
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


# Fetching products from the external API
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

with app.app_context():
    db.create_all()
    insert_products_into_db()

@app.route('/')
def home():
    products = Product.query.all()
    return render_template('index.html', products=products)

# Cart route
@app.route('/cart')
def cart():
    return render_template('cart.html')

# User personal info route
@app.route('/person')
def person():
    if 'user_id' not in session:
        flash('Please log in first!', 'warning')
        return redirect(url_for('register_and_login'))

    user = User.query.get(session['user_id'])
    return render_template('Person.html', user=user)

@app.route('/api/products')
def api_products():
    return jsonify(get_products_from_api())

# Registration and login route
@app.route('/register', methods=['GET', 'POST'])
def register_and_login():
    register_form = RegistrationForm()
    login_form = LoginForm()
    show_login_form = False

    if register_form.validate_on_submit() and 'register_submit' in request.form:
        existing_user = User.query.filter_by(email=register_form.email.data).first()
        if existing_user:
            flash('Email is already in use. Please log in.', 'danger')
            return redirect(url_for('register_and_login'))

        if register_form.password.data != register_form.confirm_password.data:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register_and_login'))

        hashed_password = bcrypt.generate_password_hash(register_form.password.data).decode('utf-8')
        user = User(name=register_form.name.data, email=register_form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        show_login_form = True

    if login_form.validate_on_submit() and 'login_submit' in request.form:
        user = User.query.filter_by(email=login_form.email.data).first()
        if not user:
            flash('No account found with this email. Please register first.', 'danger')
            return redirect(url_for('register_and_login'))

        if not bcrypt.check_password_hash(user.password, login_form.password.data):
            flash('Incorrect password.', 'danger')
            return redirect(url_for('register_and_login'))

        session['user_id'] = user.id
        session['name'] = user.name
        flash('Logged in successfully!', 'success')
        return redirect(url_for('menu'))

    return render_template('Registration.html',
                           register_form=register_form,
                           login_form=login_form,
                           show_login_form=show_login_form)

# Logout route
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.pop('name', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('register_and_login'))

@app.route('/menu')
def menu():
    if 'user_id' not in session:
        flash('Please log in first!', 'warning')
        return redirect(url_for('register_and_login'))

    products = Product.query.all()  # All products
    sold_products = SoldProduct.query.filter_by(user_id=session.get('user_id')).all()  # User's sold products
    return render_template('menu.html', products=products, sold_products=sold_products)

@app.route('/buy_product/<int:product_id>', methods=['POST'])
def buy_product(product_id):
    if 'user_id' not in session:
        flash('You must be logged in to make a purchase.', 'warning')
        return redirect(url_for('register_and_login'))

    product = Product.query.get(product_id)
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('menu'))

    try:
        # Check if the product has already been purchased by the current user
        existing_purchase = SoldProduct.query.filter_by(user_id=session['user_id'], product_id=product.id).first()
        if existing_purchase:
            existing_purchase.quantity += 1
            db.session.commit()  # Make sure changes are saved in the database
            flash(f'Product "{product.title}" updated with new quantity: {existing_purchase.quantity}.', 'success')
        else:
            sold_product = SoldProduct(
                user_id=session['user_id'],
                product_id=product.id,
                name=product.title,
                price=product.price,
                quantity=1,
                sold_at=datetime.utcnow()
            )
            db.session.add(sold_product)
            db.session.commit()  # Make sure new entry is saved
            flash(f'Product "{product.title}" successfully purchased!', 'success')

    except Exception as e:
        db.session.rollback()  # If there's an error, rollback the transaction
        flash(f"Error: {e}", 'danger')

    return redirect(url_for('menu'))


if __name__ == '__main__':
    app.run(debug=True)
