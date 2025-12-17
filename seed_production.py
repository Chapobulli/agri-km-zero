#!/usr/bin/env python3
"""Seed production database with sample data for Sardinia region"""
from app import create_app, db
from app.models import User, Product

app = create_app()

with app.app_context():
    # Check if data already exists
    if User.query.count() > 0:
        print("Database already has users, skipping seed.")
        exit(0)

    # Create sample farmers in Sardinia
    farmers_data = [
        {
            'username': 'azienda_oristano',
            'email': 'oristano@agrikmzero.it',
            'company_name': 'Azienda Agricola Oristano',
            'company_description': 'Prodotti freschi a km0 dalla provincia di Oristano. Coltiviamo con passione da 3 generazioni.',
            'address': 'Oristano, Sardegna',
            'latitude': 39.9031,
            'longitude': 8.5919,
            'is_farmer': True,
            'premium': True,
            'delivery': True
        },
        {
            'username': 'orto_cabras',
            'email': 'cabras@agrikmzero.it',
            'company_name': 'Orto di Cabras',
            'company_description': 'Ortaggi biologici certificati. Specialità: carciofi spinosi sardi.',
            'address': 'Cabras, Oristano',
            'latitude': 39.9333,
            'longitude': 8.5333,
            'is_farmer': True,
            'premium': True,
            'delivery': False
        },
        {
            'username': 'fattoria_milis',
            'email': 'milis@agrikmzero.it',
            'company_name': 'Fattoria Milis',
            'company_description': 'Produzione biologica di agrumi e ortaggi tipici sardi.',
            'address': 'Milis, Oristano',
            'latitude': 39.9500,
            'longitude': 8.6333,
            'is_farmer': True,
            'premium': True,
            'delivery': True
        }
    ]

    products_by_farmer = [
        [
            {'name': 'Pomodori di Pachino', 'description': 'Pomodori rossi siciliani dolci e succosi', 'price': 2.80, 'unit': 'kg'},
            {'name': 'Carciofi Spinosi', 'description': 'Carciofi sardi tradizionali spinosi IGP', 'price': 3.50, 'unit': 'kg'},
            {'name': 'Cassetta Mista Verdure', 'description': 'Selezione di verdure fresche di stagione', 'price': 15.00, 'unit': 'cassetta'},
        ],
        [
            {'name': 'Melanzane Violetta', 'description': 'Melanzane viola scura, polpa compatta', 'price': 3.10, 'unit': 'kg'},
            {'name': 'Zucchine Trombetta', 'description': 'Zucchine lunghe e dolci tipiche del sud', 'price': 2.90, 'unit': 'kg'},
            {'name': 'Peperoni Rossi', 'description': 'Peperoni dolci rossi carnosi', 'price': 3.20, 'unit': 'kg'},
        ],
        [
            {'name': 'Limoni di Sorrento', 'description': 'Limoni IGP profumati e ricchi di vitamina C', 'price': 2.20, 'unit': 'kg'},
            {'name': 'Arance Tarocco', 'description': 'Arance rosse dolcissime', 'price': 1.80, 'unit': 'kg'},
            {'name': 'Insalata Mista', 'description': 'Mix di insalate fresche raccolte al mattino', 'price': 8.00, 'unit': 'cassetta'},
        ]
    ]

    for i, farmer_data in enumerate(farmers_data):
        farmer = User(**farmer_data)
        farmer.set_password('demo123')
        db.session.add(farmer)
        db.session.commit()

        for product_data in products_by_farmer[i]:
            product = Product(**product_data, user_id=farmer.id)
            db.session.add(product)

    db.session.commit()
    print(f"✓ Created {len(farmers_data)} farmers with products")
    print("✓ Sample credentials: any farmer email + password 'demo123'")
