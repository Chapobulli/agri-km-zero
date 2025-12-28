"""Script per aggiornare tutti i prodotti esistenti con ordine minimo di 10 pezzi"""
from app import create_app, db
from app.models import Product

app = create_app()

with app.app_context():
    # Aggiorna tutti i prodotti esistenti
    products = Product.query.all()
    updated_count = 0
    
    for product in products:
        if product.minimum_order_quantity is None or product.minimum_order_quantity == 1:
            product.minimum_order_quantity = 10
            updated_count += 1
    
    db.session.commit()
    print(f"Aggiornati {updated_count} prodotti con ordine minimo di 10 pezzi")
