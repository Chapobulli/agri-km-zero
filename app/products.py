from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from . import db
from .models import Product
from .forms import ProductForm
import os
from werkzeug.utils import secure_filename

products = Blueprint('products', __name__)

@products.route('/products')
@login_required
def list_products():
    if current_user.is_farmer:
        products = Product.query.filter_by(user_id=current_user.id).all()
    else:
        products = Product.query.all()
    return render_template('products.html', products=products)

@products.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    if not current_user.is_farmer:
        flash('Solo agricoltori possono aggiungere prodotti.')
        return redirect(url_for('main.index'))
    form = ProductForm()
    if form.validate_on_submit():
        image_path = None
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            upload_dir = os.path.join(current_app.root_path, '..', 'static', 'uploads', 'products')
            os.makedirs(upload_dir, exist_ok=True)
            save_path = os.path.join(upload_dir, filename)
            form.image.data.save(save_path)
            image_path = f"uploads/products/{filename}"
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            unit=form.unit.data,
            image_path=image_path,
            user_id=current_user.id
        )
        db.session.add(product)
        db.session.commit()
        flash('Prodotto aggiunto!')
        return redirect(url_for('profiles.view_profile', username=current_user.username))
    return render_template('add_product.html', form=form)

@products.route('/product/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    if product.user_id != current_user.id:
        flash('Non autorizzato.')
        return redirect(url_for('main.index'))
    form = ProductForm()
    if request.method == 'GET':
        form.name.data = product.name
        form.description.data = product.description
        form.price.data = product.price
        form.unit.data = product.unit
    if form.validate_on_submit():
        product.name = form.name.data
        if form.description.data:
            product.description = form.description.data
        if form.price.data is not None:
            product.price = form.price.data
        product.unit = form.unit.data
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            upload_dir = os.path.join(current_app.root_path, '..', 'static', 'uploads', 'products')
            os.makedirs(upload_dir, exist_ok=True)
            save_path = os.path.join(upload_dir, filename)
            form.image.data.save(save_path)
            product.image_path = f"uploads/products/{filename}"
        db.session.commit()
        flash('Prodotto aggiornato!')
        return redirect(url_for('profiles.view_profile', username=current_user.username))
    return render_template('edit_product.html', form=form, product=product)

@products.route('/product/<int:product_id>/delete', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    if product.user_id != current_user.id:
        flash('Non autorizzato.')
        return redirect(url_for('main.index'))
    db.session.delete(product)
    db.session.commit()
    flash('Prodotto eliminato!')
    return redirect(url_for('profiles.view_profile', username=current_user.username))