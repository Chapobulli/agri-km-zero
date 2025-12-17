from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from . import db
from .models import User, Product
from .forms import FarmerProfileForm, ClientProfileForm
from werkzeug.utils import secure_filename
import os

profiles = Blueprint('profiles', __name__)


def save_upload(file_storage, subfolder):
    if not file_storage:
        return None
    filename = secure_filename(file_storage.filename)
    upload_dir = os.path.join(current_app.root_path, '..', 'static', 'uploads', subfolder)
    os.makedirs(upload_dir, exist_ok=True)
    save_path = os.path.join(upload_dir, filename)
    file_storage.save(save_path)
    return f"uploads/{subfolder}/{filename}"


@profiles.route('/profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if current_user.is_farmer:
        form = FarmerProfileForm()
        if request.method == 'GET':
            form.company_name.data = current_user.company_name
            form.company_description.data = current_user.company_description
            form.address.data = current_user.address
            form.latitude.data = current_user.latitude
            form.longitude.data = current_user.longitude
            form.delivery.data = current_user.delivery
        if form.validate_on_submit():
            current_user.company_name = form.company_name.data
            # Preserve existing fields if left empty
            if form.company_description.data:
                current_user.company_description = form.company_description.data
            if form.address.data:
                current_user.address = form.address.data
            if form.latitude.data is not None:
                current_user.latitude = form.latitude.data
            if form.longitude.data is not None:
                current_user.longitude = form.longitude.data
            current_user.delivery = form.delivery.data
            logo_path = save_upload(form.company_logo.data, 'profiles')
            cover_path = save_upload(form.company_cover.data, 'profiles')
            if logo_path:
                current_user.company_logo = logo_path
            if cover_path:
                current_user.company_cover = cover_path
            db.session.commit()
            flash('Profilo azienda aggiornato!')
            return redirect(url_for('profiles.view_profile', username=current_user.username))
        return render_template('profile_edit.html', farmer=True, form=form)
    else:
        form = ClientProfileForm()
        if request.method == 'GET':
            form.username.data = current_user.username
            form.bio.data = current_user.bio
            form.address.data = current_user.address
            form.latitude.data = current_user.latitude
            form.longitude.data = current_user.longitude
        if form.validate_on_submit():
            current_user.username = form.username.data
            if form.bio.data:
                current_user.bio = form.bio.data
            if form.address.data:
                current_user.address = form.address.data
            if form.latitude.data is not None:
                current_user.latitude = form.latitude.data
            if form.longitude.data is not None:
                current_user.longitude = form.longitude.data
            photo_path = save_upload(form.profile_photo.data, 'profiles')
            if photo_path:
                current_user.profile_photo = photo_path
            db.session.commit()
            flash('Profilo aggiornato!')
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
