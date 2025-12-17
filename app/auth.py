from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash
from . import db
from .models import User
from .forms import RegistrationForm, LoginForm

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, is_farmer=form.is_farmer.data)
        user.set_password(form.password.data)
        token = user.generate_verification_token()
        db.session.add(user)
        db.session.commit()
        # MVP: print verification link (add email service later)
        verify_url = url_for('auth.verify_email', token=token, _external=True)
        print(f'\n=== EMAIL VERIFICATION LINK ===\n{verify_url}\n')
        flash('Registrazione completata! Controlla i log del server per il link di verifica (MVP mode).')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('main.index'))
        flash('Credenziali non valide.')
    return render_template('login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))