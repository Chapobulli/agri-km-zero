from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from flask_login import login_required, current_user
from . import db
from .models import User, Product
from .locations import get_provinces, get_cities
from .email_utils import send_email
from geopy.distance import geodesic
import json
from datetime import datetime
import secrets
import logging

main = Blueprint('main', __name__)

@main.route('/health')
def health():
    """Lightweight health check for Render without DB query"""
    return jsonify({"status": "ok", "timestamp": datetime.utcnow().isoformat()}), 200

@main.route('/terms')
def terms():
    return render_template('terms.html')

@main.route('/privacy')
def privacy():
    return render_template('privacy.html')

@main.route('/come-funziona')
def come_funziona():
    return render_template('come_funziona.html')

@main.route('/faq')
def faq():
    return render_template('faq.html')

@main.route('/api/cities')
def api_cities():
    province = request.args.get('province', '')
    cities = get_cities(province)
    return jsonify(cities)

@main.route('/contact', methods=['GET', 'POST'])
def contact():
    """Form di contatto - invia email a llochi280@gmail.com"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()
        privacy = request.form.get('privacy')
        
        # Validazione completa
        if not all([name, email, subject, message, privacy]):
            flash('⚠️ Tutti i campi sono obbligatori e devi accettare la privacy.', 'danger')
            return redirect(url_for('main.contact'))
        
        # Invia email all'admin tramite SendGrid
        admin_email = 'llochi280@gmail.com'
        email_subject = f'Nuovo messaggio dal sito - {subject}'
        email_body = f"""
            <h3>Nuovo messaggio dal form di contatto</h3>
            <p><strong>Da:</strong> {name} ({email})</p>
            <p><strong>Oggetto:</strong> {subject}</p>
            <p><strong>Messaggio:</strong></p>
            <p>{message}</p>
            <hr>
            <p><small>Questo messaggio è stato inviato dal form di contatto di ortovicino.onrender.com</small></p>
        """
        
        # Invia email (fallback a console log se SendGrid non configurato)
        send_email(admin_email, email_subject, email_body)
        logging.info(f"Contact form: {name} ({email}) - {subject}")
        
        flash('✓ Messaggio inviato con successo! Ti risponderemo presto.', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('contact.html')

@main.route('/')
def index():
    # Get filter parameters from query string
    province_filter = request.args.get('province', '')
    city_filter = request.args.get('city', '')
    
    # Query farmers with limit for performance
    query = User.query.filter_by(is_farmer=True)
    
    # Apply filters
    if province_filter:
        query = query.filter_by(province=province_filter)
    if city_filter:
        query = query.filter_by(city=city_filter)
    
    farmers = query.limit(30).all()
    
    # Get products from filtered farmers
    farmer_ids = [f.id for f in farmers]
    products = Product.query.filter(Product.user_id.in_(farmer_ids)).all() if farmer_ids else []
    
    # Prepare data with farmer info
    products_data = []
    for product in products:
        farmer = db.session.get(User, product.user_id)
        if farmer:
            products_data.append({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': product.price,
                'unit': product.unit,
                'image_path': product.image_path,
                'farmer_name': farmer.company_name or farmer.username,
                'farmer_username': farmer.username,
                'farmer_slug': farmer.company_slug or farmer.compute_company_slug(),
                'farmer_city': farmer.city,
                'farmer_province': farmer.province,
                'farmer_address': farmer.address,
                'user_id': farmer.id
            })
    
    # Get provinces and cities for filters
    provinces = get_provinces()
    cities = get_cities(province_filter) if province_filter else []
    
    # Choose map center: default Oristano, else first farmer with coordinates
    center_lat = 39.9043
    center_lng = 8.5900
    for f in farmers:
        if f.latitude and f.longitude:
            center_lat = f.latitude
            center_lng = f.longitude
            break
    
    # Prepare farmers JSON for map
    farmers_json = json.dumps([{
        'lat': f.latitude,
        'lng': f.longitude,
        'name': f.company_name or f.username,
        'slug': f.company_slug or f.compute_company_slug(),
        'city': f.city or '',
        'province': f.province or ''
    } for f in farmers])

    return render_template('index.html', 
                         products_data=products_data,
                         farmers=farmers,
                         farmers_json=farmers_json,
                         provinces=provinces,
                         cities=cities,
                         selected_province=province_filter,
                         selected_city=city_filter,
                         center_lat=center_lat,
                         center_lng=center_lng)

@main.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'POST':
        lat = float(request.form.get('lat'))
        lng = float(request.form.get('lng'))
        radius = 50  # km
        farmers = User.query.filter_by(is_farmer=True).all()
        nearby = []
        for farmer in farmers:
            if farmer.latitude and farmer.longitude:
                dist = geodesic((lat, lng), (farmer.latitude, farmer.longitude)).km
                if dist <= radius:
                    nearby.append((farmer, dist))
        return render_template('search_results.html', nearby=nearby)
    return render_template('search.html')

@main.route('/rivendica-azienda')
def claim_search():
    """Pagina di ricerca per trovare la propria azienda"""
    query = request.args.get('q', '').strip()
    results = []
    
    if query:
        # Cerca tra profili non rivendicati
        results = User.query.filter(
            User.is_farmer == True,
            User.is_scraped == True,
            User.is_claimed == False,
            db.or_(
                User.company_name.ilike(f'%{query}%'),
                User.city.ilike(f'%{query}%'),
                User.username.ilike(f'%{query}%')
            )
        ).limit(20).all()
    
    return render_template('claim_search.html', query=query, results=results)

@main.route('/rivendica/<username>', methods=['GET', 'POST'])
def claim_business(username):
    """Pagina per rivendicare una specifica azienda"""
    company = User.query.filter_by(
        username=username,
        is_scraped=True,
        is_claimed=False
    ).first_or_404()
    
    if request.method == 'POST':
        contact_email = request.form.get('email', '').strip()
        contact_phone = request.form.get('phone', '').strip()
        
        if not contact_email:
            flash('⚠️ Email richiesta per la verifica', 'warning')
            return redirect(url_for('main.claim_business', username=username))
        
        # Genera nuovo token se non esiste
        if not company.claim_token:
            company.claim_token = secrets.token_urlsafe(32)
            db.session.commit()
        
        # TODO: Invia email di verifica (implementare quando hai servizio email)
        # send_claim_verification_email(company, contact_email, contact_phone)
        
        flash(f'✉️ Richiesta inviata! Controlla {contact_email} per il link di verifica.', 'info')
        flash('⚠️ NOTA DEMO: Sistema email non ancora configurato. Contatta info@ortovicino.it per verifica manuale.', 'warning')
        
        return redirect(url_for('main.index'))
    
    return render_template('claim_business.html', company=company)

@main.route('/verify-claim/<token>')
def verify_claim(token):
    """Verifica claim e permetti reset password"""
    company = User.query.filter_by(claim_token=token).first_or_404()
    
    if company.is_claimed:
        flash('✓ Questa azienda è già stata rivendicata', 'info')
        return redirect(url_for('main.index'))
    
    # Marca come rivendicato
    company.is_claimed = True
    company.verified_at = datetime.utcnow()
    company.data_source = 'Claimed'
    
    # Genera reset token per password
    reset_token = secrets.token_urlsafe(32)
    company.reset_token = reset_token
    
    db.session.commit()
    
    flash('✓ Azienda verificata con successo!', 'success')
    flash('🔑 Imposta ora la tua password per accedere', 'info')
    
    # Redirect a pagina reset password
    return redirect(url_for('auth.reset_password_form', token=reset_token))
