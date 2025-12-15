from app import create_app, db
from app.models import User, Product

def create_sample_data():
    app = create_app()
    with app.app_context():
        # Crea agricoltori con coordinate diverse
        farmers_data = [
            {
                'username': 'farmer_mario',
                'email': 'mario@example.com',
                'latitude': 41.9028,  # Roma
                'longitude': 12.4964,
                'address': 'Roma, Italia',
                'is_farmer': True
            },
            {
                'username': 'farmer_giuseppe',
                'email': 'giuseppe@example.com',
                'latitude': 45.4642,  # Milano
                'longitude': 9.1900,
                'address': 'Milano, Italia',
                'is_farmer': True
            },
            {
                'username': 'farmer_anna',
                'email': 'anna@example.com',
                'latitude': 40.8518,  # Napoli
                'longitude': 14.2681,
                'address': 'Napoli, Italia',
                'is_farmer': True
            }
        ]

        for farmer_data in farmers_data:
            farmer = User(**farmer_data)
            farmer.set_password('password123')
            db.session.add(farmer)
            db.session.commit()  # Commit per avere l'ID

            # Crea prodotti per ogni agricoltore
            products_data = [
                {'name': 'Pomodori Freschi', 'description': 'Pomodori rossi biologici', 'price': 2.50},
                {'name': 'Insalata Verde', 'description': 'Insalata fresca del giorno', 'price': 1.80},
                {'name': 'Zucchine', 'description': 'Zucchine croccanti', 'price': 3.20}
            ]

            for product_data in products_data:
                product = Product(**product_data, user_id=farmer.id)
                db.session.add(product)

        db.session.commit()
        print("Dati di esempio creati con successo!")

if __name__ == '__main__':
    create_sample_data()