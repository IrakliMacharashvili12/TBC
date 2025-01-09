from config import app, db,bcrypt
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from models import User, Product, SoldProduct, insert_products_into_db,get_products_from_api
from form import RegistrationForm, LoginForm
from datetime import datetime


with app.app_context():
    db.create_all()
    insert_products_into_db()


@app.route('/')
def home():
    products = Product.query.all()
    return render_template('index.html', products=products)

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

@app.route('/register', methods=['GET', 'POST'])
def register_and_login():
    register_form = RegistrationForm()
    login_form = LoginForm()
    show_login_form = False

    # Registration logic
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

    # Login logic
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
        session['email'] = user.email  # Save the email in session
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

@app.route('/admin/sold_products')
def admin_sold_products():
    if 'user_id' not in session:
        flash('Please log in first!', 'warning')
        return redirect(url_for('register_and_login'))

    user = User.query.get(session['user_id'])
    if not user or user.email != 'admin@example.com':
        flash('Access denied. You must be an admin.', 'danger')
        return redirect(url_for('menu'))

    sold_products = SoldProduct.query.all()
    total_sales = sum(product.price * product.quantity for product in sold_products)
    total_quantity = sum(product.quantity for product in sold_products)
    return render_template(
        'admin_sold_products.html',
        sold_products=sold_products,
        total_sales=total_sales,
        total_quantity=total_quantity
    )
