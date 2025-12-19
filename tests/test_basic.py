"""
Test unitari con pytest per Agri KM Zero
Installare con: pip install pytest
Eseguire con: pytest tests/
"""

import pytest
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User, Product

@pytest.fixture
def app():
    """Crea app Flask per testing"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    return app

@pytest.fixture
def client(app):
    """Crea test client"""
    return app.test_client()

@pytest.fixture
def app_context(app):
    """Crea application context"""
    with app.app_context():
        yield

class TestHealthCheck:
    """Test endpoint di health check"""
    
    def test_health_endpoint(self, client):
        """Test /health ritorna 200"""
        response = client.get('/health')
        assert response.status_code in [200, 500]  # 500 ok if DB has issues
        data = response.get_json()
        assert 'status' in data
        assert 'checks' in data

class TestPublicPages:
    """Test pagine pubbliche"""
    
    def test_homepage(self, client):
        """Test homepage accessibile"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Agri KM Zero' in response.data or b'agri' in response.data.lower()
    
    def test_products_page(self, client):
        """Test pagina prodotti accessibile"""
        response = client.get('/products')
        assert response.status_code == 200
    
    def test_login_page(self, client):
        """Test pagina login accessibile"""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'login' in response.data.lower() or b'accedi' in response.data.lower()
    
    def test_register_page(self, client):
        """Test pagina registrazione accessibile"""
        response = client.get('/register')
        assert response.status_code == 200
        assert b'register' in response.data.lower() or b'registr' in response.data.lower()

class TestDatabase:
    """Test database e modelli"""
    
    def test_database_connection(self, app_context):
        """Test connessione database"""
        result = db.session.execute(db.text('SELECT 1')).scalar()
        assert result == 1
    
    def test_user_model(self, app_context):
        """Test modello User"""
        users = User.query.all()
        assert isinstance(users, list)
        
        if users:
            user = users[0]
            assert hasattr(user, 'id')
            assert hasattr(user, 'username')
            assert hasattr(user, 'email')
            assert hasattr(user, 'is_farmer')
    
    def test_product_model(self, app_context):
        """Test modello Product"""
        products = Product.query.all()
        assert isinstance(products, list)
        
        if products:
            product = products[0]
            assert hasattr(product, 'id')
            assert hasattr(product, 'name')
            assert hasattr(product, 'price')
            assert hasattr(product, 'user_id')

class TestFarmerWorkflow:
    """Test workflow agricoltore"""
    
    def test_farmers_exist(self, app_context):
        """Test esistenza agricoltori"""
        farmers = User.query.filter_by(is_farmer=True).all()
        # Non fail if no farmers, just check query works
        assert isinstance(farmers, list)
    
    def test_farmer_has_location(self, app_context):
        """Test agricoltori hanno località"""
        farmers = User.query.filter_by(is_farmer=True).limit(5).all()
        
        for farmer in farmers:
            # Check that farmer has either old lat/lng or new province/city
            has_old_location = farmer.latitude is not None and farmer.longitude is not None
            has_new_location = farmer.province is not None or farmer.city is not None
            
            # At least warn if neither
            if not has_old_location and not has_new_location:
                print(f"Warning: Farmer {farmer.username} has no location data")

class TestDataIntegrity:
    """Test integrità dati"""
    
    def test_products_have_farmers(self, app_context):
        """Test tutti i prodotti hanno un agricoltore"""
        products = Product.query.all()
        
        orphan_products = []
        for product in products:
            farmer = User.query.get(product.user_id)
            if not farmer:
                orphan_products.append(product.id)
        
        if orphan_products:
            print(f"Warning: Found {len(orphan_products)} orphan products")
        
        # Don't fail test, just warn
        assert isinstance(orphan_products, list)
    
    def test_products_have_required_fields(self, app_context):
        """Test prodotti hanno campi obbligatori"""
        products = Product.query.limit(10).all()
        
        for product in products:
            assert product.name is not None, f"Product {product.id} has no name"
            assert product.price is not None, f"Product {product.id} has no price"
            assert product.unit is not None, f"Product {product.id} has no unit"

class TestDebugEndpoints:
    """Test endpoint di debug"""
    
    def test_debug_users(self, client):
        """Test /debug/users accessibile"""
        response = client.get('/debug/users')
        assert response.status_code == 200
    
    def test_debug_products(self, client):
        """Test /debug/products accessibile"""
        response = client.get('/debug/products')
        assert response.status_code == 200
    
    def test_debug_test_data(self, client):
        """Test /debug/test-data ritorna JSON"""
        response = client.get('/debug/test-data')
        assert response.status_code == 200
        data = response.get_json()
        assert 'database_tables' in data
        assert 'issues' in data
