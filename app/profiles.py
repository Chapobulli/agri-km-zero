from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from . import db
from .models import User, Product, OrderRequest
from .forms import FarmerProfileForm, ClientProfileForm
from .locations import get_provinces, get_cities
from werkzeug.utils import secure_filename
import os
import re

profiles = Blueprint('profiles', __name__)


def save_upload(file_storage, subfolder):
    if not file_storage:
        return None
    import cloudinary.uploader
    upload_result = cloudinary.uploader.upload(file_storage, folder=f"agri_km_zero/{subfolder}")
    return upload_result['secure_url']


@profiles.route('/profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if current_user.is_farmer:
        form = FarmerProfileForm()
        # Populate province choices
        form.province.choices = [('', 'Seleziona Provincia')] + [(p, p) for p in get_provinces()]
        # Populate city choices based on selected province
        if form.province.data:
            form.city.choices = [('', 'Seleziona Comune')] + [(c, c) for c in get_cities(form.province.data)]
        else:
            form.city.choices = [('', 'Seleziona prima la provincia')]
        
        if request.method == 'GET':
            form.username.data = current_user.username
            form.display_name.data = current_user.display_name
            form.phone.data = current_user.phone
            form.company_name.data = current_user.company_name
            form.company_description.data = current_user.company_description
            form.province.data = current_user.province
            form.city.data = current_user.city
            # Reload cities for GET with existing province
            if current_user.province:
                form.city.choices = [('', 'Seleziona Comune')] + [(c, c) for c in get_cities(current_user.province)]
            form.address.data = current_user.address
            form.delivery.data = current_user.delivery
        if form.validate_on_submit():
            # Validazione custom: se provincia è selezionata, anche comune deve esserlo
            if form.province.data and not form.city.data:
                flash('⚠ Seleziona un comune dalla provincia scelta', 'warning')
                return render_template('profile_edit.html', farmer=True, form=form)
            
            current_user.username = form.username.data
            if form.display_name.data:
                current_user.display_name = form.display_name.data
            current_user.phone = form.phone.data
            current_user.company_name = form.company_name.data
            current_user.province = form.province.data
            current_user.city = form.city.data
            # Preserve existing fields if left empty
            if form.company_description.data:
                current_user.company_description = form.company_description.data
            if form.address.data:
                current_user.address = form.address.data
            current_user.delivery = form.delivery.data
            # Aggiorna slug azienda (unico, basato su nome azienda)
            if current_user.is_farmer:
                base_slug = slugify(current_user.company_name or current_user.username)
                current_user.company_slug = ensure_unique_slug(base_slug, current_user.id)
            logo_path = save_upload(form.company_logo.data, 'profiles')
            cover_path = save_upload(form.company_cover.data, 'profiles')
            if logo_path:
                current_user.company_logo = logo_path
            if cover_path:
                current_user.company_cover = cover_path
            db.session.commit()
            flash('✓ Profilo azienda aggiornato con successo!', 'success')
            return redirect(url_for('profiles.view_company', slug=current_user.company_slug))
        return render_template('profile_edit.html', farmer=True, form=form)
    else:
        form = ClientProfileForm()
        if request.method == 'GET':
            form.username.data = current_user.username
            form.display_name.data = current_user.display_name
            form.bio.data = current_user.bio
            form.address.data = current_user.address
        if form.validate_on_submit():
            current_user.username = form.username.data
            if form.display_name.data:
                current_user.display_name = form.display_name.data
            if form.bio.data:
                current_user.bio = form.bio.data
            if form.address.data:
                current_user.address = form.address.data
            photo_path = save_upload(form.profile_photo.data, 'profiles')
            if photo_path:
                current_user.profile_photo = photo_path
            db.session.commit()
            flash('✓ Profilo aggiornato con successo!', 'success')
            return redirect(url_for('profiles.view_profile', username=current_user.username))
        return render_template('profile_edit.html', farmer=False, form=form)


def slugify(value):
    slug = re.sub(r'[^a-zA-Z0-9]+', '-', value or '').strip('-').lower()
    return slug or None


def ensure_unique_slug(base_slug, user_id):
    if not base_slug:
        base_slug = f"azienda-{user_id}"
    existing = User.query.filter(User.company_slug == base_slug, User.id != user_id).first()
    if existing:
        return f"{base_slug}-{user_id}"
    return base_slug


def get_farmer_by_slug(slug):
    # Try direct match on stored slug
    farmer = User.query.filter_by(company_slug=slug, is_farmer=True).first()
    if farmer:
        return farmer
    # Try to compute slug for farmers missing the field
    missing_slug_farmers = User.query.filter_by(is_farmer=True, company_slug=None).all()
    for f in missing_slug_farmers:
        computed = ensure_unique_slug(slugify(f.company_name or f.username), f.id)
        if computed == slug:
            f.company_slug = computed
            db.session.commit()
            return f
    return None


@profiles.route('/c/<slug>')
def view_company(slug):
    user = get_farmer_by_slug(slug)
    if not user:
        # fallback: maybe passed username directly
        user = User.query.filter_by(username=slug, is_farmer=True).first_or_404()
        if not user.company_slug:
            user.company_slug = ensure_unique_slug(slugify(user.company_name or user.username), user.id)
            db.session.commit()
        return redirect(url_for('profiles.view_company', slug=user.company_slug))
    products = Product.query.filter_by(user_id=user.id).all()
    orders = OrderRequest.query.filter_by(farmer_id=user.id).order_by(OrderRequest.created_at.desc()).all()
    return render_template('profile.html', user=user, products=products, orders=orders, farmer=True)


@profiles.route('/u/<username>')
def view_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user.is_farmer:
        if user.company_slug:
            return redirect(url_for('profiles.view_company', slug=user.company_slug))
        else:
            # generate slug on the fly
            user.company_slug = ensure_unique_slug(slugify(user.company_name or user.username), user.id)
            db.session.commit()
            return redirect(url_for('profiles.view_company', slug=user.company_slug))
    # non farmer profile
    return render_template('profile.html', user=user, farmer=False)

@profiles.route('/my-orders')
@login_required
def my_orders():
    if not current_user.is_farmer:
        flash('Solo gli agricoltori possono visualizzare gli ordini ricevuti', 'warning')
        return redirect(url_for('main.index'))
    orders = OrderRequest.query.filter_by(farmer_id=current_user.id).order_by(OrderRequest.created_at.desc()).all()
    return render_template('my_orders.html', orders=orders)

@profiles.route('/my-client-orders')
@login_required
def my_client_orders():
    orders = OrderRequest.query.filter_by(client_id=current_user.id).order_by(OrderRequest.created_at.desc()).all()
    return render_template('my_client_orders.html', orders=orders)


@profiles.route('/companies')
def companies():
    farmers = User.query.filter_by(is_farmer=True).all()
    updated = False
    for f in farmers:
        if not f.company_slug:
            f.company_slug = ensure_unique_slug(slugify(f.company_name or f.username), f.id)
            updated = True
    if updated:
        db.session.commit()
    return render_template('companies.html', farmers=farmers)
