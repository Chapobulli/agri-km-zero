from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from . import db
from .models import Product
from .forms import ProductForm

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
    if not current_user.premium:
        flash('Devi avere un account premium per pubblicare prodotti.')
        return redirect(url_for('main.index'))
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(name=form.name.data, description=form.description.data, price=form.price.data, user_id=current_user.id)
        db.session.add(product)
        db.session.commit()
        flash('Prodotto aggiunto!')
        return redirect(url_for('products.list_products'))
    return render_template('add_product.html', form=form)