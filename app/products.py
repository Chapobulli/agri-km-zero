from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from . import db
from .models import Product, User
from .forms import ProductForm
import os
from werkzeug.utils import secure_filename

products = Blueprint('products', __name__)

@products.route('/products')
def list_products():
    # Pagina pubblica - mostra tutti i prodotti
    all_products = Product.query.all()
    # Add farmer info to each product
    products_data = []
    for p in all_products:
        farmer = db.session.get(User, p.user_id)
        products_data.append({
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'price': p.price,
            'unit': p.unit,
            'image_path': p.image_path,
            'user_id': p.user_id,
            'farmer_name': farmer.company_name if farmer and farmer.company_name else (farmer.username if farmer else 'Sconosciuto'),
            'farmer_username': farmer.username if farmer else None,
            'farmer_slug': farmer.company_slug if farmer else None,
            'farmer_city': farmer.city if farmer else None,
            'farmer_province': farmer.province if farmer else None
        })
    return render_template('products.html', products=products_data)

@products.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    if not current_user.is_farmer:
        flash('⚠ Solo agricoltori possono aggiungere prodotti.', 'warning')
        return redirect(url_for('main.index'))
    form = ProductForm()
    if form.validate_on_submit():
        image_path = None
        if form.image.data:
            import cloudinary.uploader
            upload_result = cloudinary.uploader.upload(form.image.data, folder="agri_km_zero/products")
            image_path = upload_result['secure_url']
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
        flash('✓ Prodotto aggiunto con successo!', 'success')
        return redirect(url_for('profiles.view_company', slug=current_user.company_slug or current_user.compute_company_slug()))
    return render_template('add_product.html', form=form)

@products.route('/product/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    if product.user_id != current_user.id:
        flash('⚠ Non autorizzato.', 'danger')
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
            import cloudinary.uploader
            upload_result = cloudinary.uploader.upload(form.image.data, folder="agri_km_zero/products")
            product.image_path = upload_result['secure_url']
        db.session.commit()
        flash('✓ Prodotto aggiornato con successo!', 'success')
        return redirect(url_for('profiles.view_company', slug=current_user.company_slug or current_user.compute_company_slug()))
    return render_template('edit_product.html', form=form, product=product)

@products.route('/product/<int:product_id>/delete', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    if product.user_id != current_user.id:
        flash('⚠ Non autorizzato.', 'danger')
        return redirect(url_for('main.index'))
    db.session.delete(product)
    db.session.commit()
    flash('✓ Prodotto eliminato con successo!', 'success')
    return redirect(url_for('profiles.view_company', slug=current_user.company_slug or current_user.compute_company_slug()))