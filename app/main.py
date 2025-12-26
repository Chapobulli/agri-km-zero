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

    return render_template('index.html', 
                         products_data=products_data,
                         farmers=farmers,
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