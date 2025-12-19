from flask import Blueprint, jsonify, render_template_string
from flask_login import current_user
from . import db
from .models import User, Product, Message
from sqlalchemy import text
import sys

debug = Blueprint('debug', __name__)

@debug.route('/health')
def health_check():
    """Endpoint per verificare lo stato dell'applicazione"""
    checks = {
        'status': 'healthy',
        'python_version': sys.version,
        'checks': {}
    }
    
    # Test database connection
    try:
        db.session.execute(text('SELECT 1'))
        checks['checks']['database'] = 'OK'
    except Exception as e:
        checks['checks']['database'] = f'ERROR: {str(e)}'
        checks['status'] = 'unhealthy'
    
    # Count records
    try:
        checks['checks']['users_count'] = User.query.count()
        checks['checks']['farmers_count'] = User.query.filter_by(is_farmer=True).count()
        checks['checks']['products_count'] = Product.query.count()
        checks['checks']['messages_count'] = Message.query.count()
    except Exception as e:
        checks['checks']['counts'] = f'ERROR: {str(e)}'
        checks['status'] = 'unhealthy'
    
    # Test user authentication
    checks['checks']['current_user'] = {
        'authenticated': current_user.is_authenticated,
        'id': current_user.id if current_user.is_authenticated else None,
        'username': current_user.username if current_user.is_authenticated else None
    }
    
    return jsonify(checks), 200 if checks['status'] == 'healthy' else 500

@debug.route('/debug/users')
def debug_users():
    """Mostra info debug su tutti gli utenti"""
    users = User.query.all()
    users_data = []
    for u in users:
        users_data.append({
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'is_farmer': u.is_farmer,
            'email_verified': u.email_verified,
            'company_name': u.company_name,
            'province': u.province,
            'city': u.city,
            'address': u.address,
            'products_count': Product.query.filter_by(user_id=u.id).count()
        })
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Debug Users</title>
        <style>
            body { font-family: monospace; padding: 20px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #4CAF50; color: white; }
            tr:nth-child(even) { background-color: #f2f2f2; }
            .farmer { background-color: #c8e6c9; }
            .client { background-color: #bbdefb; }
        </style>
    </head>
    <body>
        <h1>Debug: Users ({{ users|length }})</h1>
        <table>
            <tr>
                <th>ID</th>
                <th>Username</th>
                <th>Email</th>
                <th>Type</th>
                <th>Verified</th>
                <th>Company</th>
                <th>Location</th>
                <th>Address</th>
                <th>Products</th>
            </tr>
            {% for u in users %}
            <tr class="{{ 'farmer' if u.is_farmer else 'client' }}">
                <td>{{ u.id }}</td>
                <td>{{ u.username }}</td>
                <td>{{ u.email }}</td>
                <td>{{ 'Agricoltore' if u.is_farmer else 'Cliente' }}</td>
                <td>{{ '✓' if u.email_verified else '✗' }}</td>
                <td>{{ u.company_name or '-' }}</td>
                <td>{{ u.city or '-' }}, {{ u.province or '-' }}</td>
                <td>{{ u.address or '-' }}</td>
                <td>{{ u.products_count }}</td>
            </tr>
            {% endfor %}
        </table>
        <br>
        <a href="/debug/products">View Products</a> | 
        <a href="/health">Health Check</a> |
        <a href="/">Home</a>
    </body>
    </html>
    """
    
    return render_template_string(html, users=users_data)

@debug.route('/debug/products')
def debug_products():
    """Mostra info debug su tutti i prodotti"""
    products = Product.query.all()
    products_data = []
    for p in products:
        farmer = User.query.get(p.user_id)
        products_data.append({
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'price': p.price,
            'unit': p.unit,
            'image_path': p.image_path,
            'user_id': p.user_id,
            'farmer_username': farmer.username if farmer else 'DELETED',
            'farmer_company': farmer.company_name if farmer else None,
            'farmer_location': f"{farmer.city}, {farmer.province}" if farmer and farmer.city else None
        })
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Debug Products</title>
        <style>
            body { font-family: monospace; padding: 20px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #4CAF50; color: white; }
            tr:nth-child(even) { background-color: #f2f2f2; }
            .has-image { background-color: #e8f5e9; }
            .no-image { background-color: #ffebee; }
            img { max-height: 50px; }
        </style>
    </head>
    <body>
        <h1>Debug: Products ({{ products|length }})</h1>
        <table>
            <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Description</th>
                <th>Price</th>
                <th>Unit</th>
                <th>Image</th>
                <th>Farmer</th>
                <th>Company</th>
                <th>Location</th>
            </tr>
            {% for p in products %}
            <tr class="{{ 'has-image' if p.image_path else 'no-image' }}">
                <td>{{ p.id }}</td>
                <td>{{ p.name }}</td>
                <td>{{ (p.description[:50] + '...') if p.description and p.description|length > 50 else (p.description or '-') }}</td>
                <td>{{ '%.2f'|format(p.price) }} €</td>
                <td>{{ p.unit }}</td>
                <td>
                    {% if p.image_path %}
                        <img src="{{ p.image_path }}" alt="img">
                    {% else %}
                        -
                    {% endif %}
                </td>
                <td>{{ p.farmer_username }}</td>
                <td>{{ p.farmer_company or '-' }}</td>
                <td>{{ p.farmer_location or '-' }}</td>
            </tr>
            {% endfor %}
        </table>
        <br>
        <a href="/debug/users">View Users</a> | 
        <a href="/health">Health Check</a> |
        <a href="/">Home</a>
    </body>
    </html>
    """
    
    return render_template_string(html, products=products_data)

@debug.route('/debug/test-data')
def test_data():
    """Mostra dati di test per verificare problemi"""
    data = {
        'database_tables': [],
        'sample_user': None,
        'sample_product': None,
        'issues': []
    }
    
    # Get table names
    try:
        inspector = db.inspect(db.engine)
        data['database_tables'] = inspector.get_table_names()
    except Exception as e:
        data['issues'].append(f"Cannot inspect tables: {str(e)}")
    
    # Get sample user
    try:
        user = User.query.first()
        if user:
            data['sample_user'] = {
                'id': user.id,
                'username': user.username,
                'is_farmer': user.is_farmer,
                'has_province': bool(user.province),
                'has_city': bool(user.city),
                'has_address': bool(user.address)
            }
        else:
            data['issues'].append("No users found in database")
    except Exception as e:
        data['issues'].append(f"Cannot query users: {str(e)}")
    
    # Get sample product
    try:
        product = Product.query.first()
        if product:
            data['sample_product'] = {
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'user_id': product.user_id,
                'has_image': bool(product.image_path)
            }
        else:
            data['issues'].append("No products found in database")
    except Exception as e:
        data['issues'].append(f"Cannot query products: {str(e)}")
    
    return jsonify(data)
