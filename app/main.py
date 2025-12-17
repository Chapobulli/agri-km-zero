from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from . import db
from .models import User, Product
from geopy.distance import geodesic

main = Blueprint('main', __name__)

@main.route('/terms')
def terms():
    return render_template('terms.html')

@main.route('/privacy')
def privacy():
    return render_template('privacy.html')

@main.route('/')
def index():
    # Posizione di riferimento (Oristano, Sardegna)
    reference_location = (39.9031, 8.5919)  # Oristano coordinates

    # Prendi alcuni prodotti recenti con le loro distanze
    products = Product.query.join(User).filter(User.is_farmer == True).limit(6).all()

    products_with_distance = []
    for product in products:
        if product.farmer.latitude and product.farmer.longitude:
            farmer_location = (product.farmer.latitude, product.farmer.longitude)
            distance = geodesic(reference_location, farmer_location).km
            products_with_distance.append({
                'product': product,
                'farmer': product.farmer,
                'distance': round(distance, 1)
            })

    # Ordina per distanza
    products_with_distance.sort(key=lambda x: x['distance'])

    return render_template('index.html', nearby_products=products_with_distance)

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