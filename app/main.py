from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from . import db
from .models import User, Product
from geopy.distance import geodesic

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

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