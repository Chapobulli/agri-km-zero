import os
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from . import db
from .models import User
from .forms import RegistrationForm, LoginForm
from .email_utils import send_email

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Prevent duplicate email/username with a friendly message
        existing = User.query.filter(
            or_(User.email == form.email.data, User.username == form.username.data)
        ).first()
        if existing:
            if existing.email == form.email.data:
                flash('⚠ Questa email è già registrata. Prova ad accedere o recuperare la password.', 'warning')
            else:
                flash('⚠ Questo username è già in uso. Scegline un altro.', 'warning')
            return render_template('register.html', form=form)

        user = User(username=form.username.data, email=form.email.data, is_farmer=form.is_farmer.data)
        user.set_password(form.password.data)
        token = user.generate_verification_token()
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('⚠ Email o username già in uso. Riprova con credenziali diverse.', 'danger')
            return render_template('register.html', form=form)

        # Build verification URL (prefer APP_BASE_URL if provided)
        base_url = os.environ.get('APP_BASE_URL')
        path_only = url_for('auth.verify_email', token=token, _external=False)
        verify_url = (base_url.rstrip('/') + path_only) if base_url else url_for('auth.verify_email', token=token, _external=True)

        # Send verification email (falls back to logging if not configured)
        email_body = f"""
            <p>Ciao {user.username},</p>
            <p>Conferma la tua email per attivare l'account su Agri KM Zero:</p>
            <p><a href="{verify_url}">Verifica la tua email</a></p>
            <p>Se non hai richiesto tu questa registrazione, ignora questa email.</p>
        """
        send_email(user.email, 'Verifica la tua email - Agri KM Zero', email_body)
        flash('✓ Registrazione completata! Ti abbiamo inviato un\'email per verificare il tuo account.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f'✓ Benvenuto {user.username}!', 'success')
            return redirect(url_for('main.index'))
        flash('⚠ Credenziali non valide.', 'danger')
    return render_template('login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('✓ Logout effettuato con successo. A presto!', 'info')
    return redirect(url_for('main.index'))

@auth.route('/verify/<token>')
def verify_email(token):
    user = User.query.filter_by(verification_token=token).first()
    if not user:
        flash('⚠ Link di verifica non valido o scaduto.', 'warning')
        return redirect(url_for('auth.login'))
    user.email_verified = True
    user.verification_token = None
    db.session.commit()
    flash('✓ Email verificata con successo! Ora puoi accedere.', 'success')
    return redirect(url_for('auth.login'))

@auth.route('/request-reset', methods=['GET', 'POST'])
def request_reset():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('✓ Se l\'email esiste, invieremo un link di reset.', 'info')
            return redirect(url_for('auth.login'))
        token = user.generate_reset_token()
        db.session.commit()
        base_url = os.environ.get('APP_BASE_URL')
        path_only = url_for('auth.reset_password', token=token, _external=False)
        reset_url = (base_url.rstrip('/') + path_only) if base_url else url_for('auth.reset_password', token=token, _external=True)
        email_body = f"""
            <p>Ciao {user.username},</p>
            <p>Per reimpostare la tua password clicca sul link:</p>
            <p><a href="{reset_url}">Reimposta la password</a></p>
            <p>Se non l’hai richiesto tu, ignora questa email.</p>
        """
        send_email(user.email, 'Reset password - Agri KM Zero', email_body)
        flash('✓ Se l\'email esiste, invieremo un link di reset.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('request_reset.html')

@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.query.filter_by(reset_token=token).first()
    if not user:
        flash('⚠ Link di reset non valido o scaduto.', 'warning')
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        pwd = request.form.get('password')
        confirm = request.form.get('confirm_password')
        if not pwd or pwd != confirm:
            flash('⚠ Le password non coincidono.', 'danger')
            return render_template('reset_password.html')
        user.set_password(pwd)
        user.reset_token = None
        db.session.commit()
        flash('✓ Password aggiornata con successo. Puoi accedere.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('reset_password.html')