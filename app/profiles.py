from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from . import db
from .models import User, Product
from .forms import FarmerProfileForm, ClientProfileForm
from .locations import get_provinces, get_cities
from werkzeug.utils import secure_filename
import os

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
            current_user.company_name = form.company_name.data
            current_user.province = form.province.data
            current_user.city = form.city.data
            # Preserve existing fields if left empty
            if form.company_description.data:
                current_user.company_description = form.company_description.data
            if form.address.data:
                current_user.address = form.address.data
            current_user.delivery = form.delivery.data
            logo_path = save_upload(form.company_logo.data, 'profiles')
            cover_path = save_upload(form.company_cover.data, 'profiles')
            if logo_path:
                current_user.company_logo = logo_path
            if cover_path:
                current_user.company_cover = cover_path
            db.session.commit()
            flash('✓ Profilo azienda aggiornato con successo!', 'success')
            return redirect(url_for('profiles.view_profile', username=current_user.username))
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


@profiles.route('/u/<username>')
def view_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user.is_farmer:
        # Load products for company page
        products = Product.query.filter_by(user_id=user.id).all()
        return render_template('profile.html', user=user, products=products, farmer=True)
    else:
        return render_template('profile.html', user=user, farmer=False)


@profiles.route('/companies')
def companies():
    farmers = User.query.filter_by(is_farmer=True).all()
    return render_template('companies.html', farmers=farmers)
