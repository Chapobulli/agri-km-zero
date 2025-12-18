from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from . import db
from .models import User, Product
from .locations import get_provinces, get_cities
from geopy.distance import geodesic

main = Blueprint('main', __name__)

@main.route('/terms')
def terms():
    return render_template('terms.html')

@main.route('/privacy')
def privacy():
    return render_template('privacy.html')

@main.route('/api/cities')
def api_cities():
    province = request.args.get('province', '')
    cities = get_cities(province)
    return jsonify(cities)

@main.route('/')
def index():
    # Get filter parameters from query string
    province_filter = request.args.get('province', '')
    city_filter = request.args.get('city', '')
    
    # Start with all farmers
    query = User.query.filter_by(is_farmer=True)
    
    # Apply filters
    if province_filter:
        query = query.filter_by(province=province_filter)
    if city_filter:
        query = query.filter_by(city=city_filter)
    
    farmers = query.all()
    
    # Get products from filtered farmers
    farmer_ids = [f.id for f in farmers]
    products = Product.query.filter(Product.user_id.in_(farmer_ids)).all() if farmer_ids else []
    
    # Prepare data with farmer info
    products_data = []
    for product in products:
        products_data.append({
            'product': product,
            'farmer': product.farmer
        })
    
    # Get provinces and cities for filters
    provinces = get_provinces()
    cities = get_cities(province_filter) if province_filter else []
    
    return render_template('index.html', 
                         products_data=products_data,
                         farmers=farmers,
                         provinces=provinces,
                         cities=cities,
                         selected_province=province_filter,
                         selected_city=city_filter)

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