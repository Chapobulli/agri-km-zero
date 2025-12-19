"""
Script di test per verificare il funzionamento dell'app Agri KM Zero
Esegui con: python test_app.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models import User, Product, Message

def test_database_connection():
    """Test 1: Verifica connessione database"""
    print("\n🔍 Test 1: Database Connection")
    try:
        app = create_app()
        with app.app_context():
            db.session.execute(db.text('SELECT 1'))
            print("✅ Database connection OK")
            return True
    except Exception as e:
        print(f"❌ Database connection FAILED: {e}")
        return False

def test_models():
    """Test 2: Verifica modelli database"""
    print("\n🔍 Test 2: Database Models")
    try:
        app = create_app()
        with app.app_context():
            user_count = User.query.count()
            farmer_count = User.query.filter_by(is_farmer=True).count()
            product_count = Product.query.count()
            message_count = Message.query.count()
            
            print(f"✅ Users: {user_count} (Farmers: {farmer_count})")
            print(f"✅ Products: {product_count}")
            print(f"✅ Messages: {message_count}")
            return True
    except Exception as e:
        print(f"❌ Models test FAILED: {e}")
        return False

def test_data_integrity():
    """Test 3: Verifica integrità dati"""
    print("\n🔍 Test 3: Data Integrity")
    issues = []
    
    try:
        app = create_app()
        with app.app_context():
            # Check users without required fields
            users = User.query.all()
            for user in users:
                if user.is_farmer:
                    if not user.province or not user.city:
                        issues.append(f"Farmer {user.username} (ID: {user.id}) missing location")
            
            # Check products without farmers
            products = Product.query.all()
            for product in products:
                farmer = User.query.get(product.user_id)
                if not farmer:
                    issues.append(f"Product {product.name} (ID: {product.id}) has no farmer")
                elif not farmer.is_farmer:
                    issues.append(f"Product {product.name} belongs to non-farmer {farmer.username}")
            
            if issues:
                print("⚠️  Data integrity issues found:")
                for issue in issues:
                    print(f"   - {issue}")
                return False
            else:
                print("✅ All data integrity checks passed")
                return True
    except Exception as e:
        print(f"❌ Data integrity test FAILED: {e}")
        return False

def test_routes():
    """Test 4: Verifica routes principali"""
    print("\n🔍 Test 4: Main Routes")
    try:
        app = create_app()
        client = app.test_client()
        
        routes_to_test = [
            ('/', 'Homepage'),
            ('/products', 'Products page'),
            ('/login', 'Login page'),
            ('/register', 'Register page'),
            ('/health', 'Health check'),
        ]
        
        all_ok = True
        for route, name in routes_to_test:
            response = client.get(route)
            if response.status_code == 200:
                print(f"✅ {name}: {route} - OK")
            else:
                print(f"❌ {name}: {route} - Status {response.status_code}")
                all_ok = False
        
        return all_ok
    except Exception as e:
        print(f"❌ Routes test FAILED: {e}")
        return False

def test_farmer_profiles():
    """Test 5: Verifica profili agricoltori"""
    print("\n🔍 Test 5: Farmer Profiles")
    try:
        app = create_app()
        with app.app_context():
            farmers = User.query.filter_by(is_farmer=True).all()
            
            if not farmers:
                print("⚠️  No farmers found in database")
                return True
            
            print(f"📊 Found {len(farmers)} farmer(s)")
            
            for farmer in farmers:
                issues = []
                if not farmer.company_name:
                    issues.append("No company name")
                if not farmer.province:
                    issues.append("No province")
                if not farmer.city:
                    issues.append("No city")
                if not farmer.address:
                    issues.append("No address")
                
                product_count = Product.query.filter_by(user_id=farmer.id).count()
                
                status = "⚠️ " if issues else "✅"
                print(f"{status} {farmer.username} (ID: {farmer.id})")
                print(f"   Company: {farmer.company_name or 'N/A'}")
                print(f"   Location: {farmer.city or 'N/A'}, {farmer.province or 'N/A'}")
                print(f"   Products: {product_count}")
                if issues:
                    print(f"   Issues: {', '.join(issues)}")
            
            return True
    except Exception as e:
        print(f"❌ Farmer profiles test FAILED: {e}")
        return False

def test_products_display():
    """Test 6: Verifica visualizzazione prodotti"""
    print("\n🔍 Test 6: Products Display")
    try:
        app = create_app()
        with app.app_context():
            products = Product.query.all()
            
            if not products:
                print("⚠️  No products found in database")
                return True
            
            print(f"📊 Found {len(products)} product(s)")
            
            all_ok = True
            for product in products:
                farmer = User.query.get(product.user_id)
                issues = []
                
                if not product.name:
                    issues.append("No name")
                if product.price is None:
                    issues.append("No price")
                if not product.unit:
                    issues.append("No unit")
                if not farmer:
                    issues.append("No farmer found")
                
                status = "⚠️ " if issues else "✅"
                print(f"{status} {product.name} (ID: {product.id})")
                print(f"   Price: {product.price if product.price is not None else 'N/A'} €/{product.unit or 'N/A'}")
                print(f"   Farmer: {farmer.username if farmer else 'DELETED'}")
                print(f"   Image: {'Yes' if product.image_path else 'No'}")
                if issues:
                    print(f"   Issues: {', '.join(issues)}")
                    all_ok = False
            
            return all_ok
    except Exception as e:
        print(f"❌ Products display test FAILED: {e}")
        return False

def main():
    """Esegue tutti i test"""
    print("=" * 60)
    print("🧪 AGRI KM ZERO - TEST SUITE")
    print("=" * 60)
    
    tests = [
        test_database_connection,
        test_models,
        test_data_integrity,
        test_routes,
        test_farmer_profiles,
        test_products_display
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append((test_func.__name__, result))
        except Exception as e:
            print(f"❌ {test_func.__name__} crashed: {e}")
            results.append((test_func.__name__, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
