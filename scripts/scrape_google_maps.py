"""
Script per importare aziende agricole da Google Maps API
Uso: python scripts/scrape_google_maps.py

NOTA LEGALE E GDPR:
- I dati vengono raccolti da fonti pubbliche (Google Maps)
- Sono usati per creare profili "unclaimed" che i proprietari possono rivendicare
- Conforme a GDPR Art.14 (dati raccolti da fonti pubbliche con trasparenza)
- I proprietari possono richiedere rimozione dati in qualsiasi momento

REQUISITI:
1. API Key Google Maps Places API attiva
2. Impostare GOOGLE_MAPS_API_KEY nelle variabili d'ambiente o in .env
3. pip install googlemaps

Termini di Servizio Google Maps:
- Rispettare rate limits (https://developers.google.com/maps/documentation/places/web-service/usage-and-billing)
- Attribution richiesta (già inclusa nel footer del sito)
- Dati non possono essere redistribuiti raw, ma possono essere usati per creare derivati
"""

import os
import sys
import secrets
import re
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    import googlemaps
except ImportError:
    print("ERROR: googlemaps package not found. Install with: pip install googlemaps")
    sys.exit(1)

from app import create_app, db
from app.models import User

# Configurazione
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
if not GOOGLE_MAPS_API_KEY:
    print("ERROR: GOOGLE_MAPS_API_KEY not set. Get one from: https://console.cloud.google.com/")
    print("Enable 'Places API' in your Google Cloud Console project")
    sys.exit(1)

# Aree target (provincie Sardegna)
TARGET_PROVINCES = [
    'Cagliari', 'Sassari', 'Oristano', 'Nuoro', 'Sud Sardegna'
]

# Query di ricerca
SEARCH_QUERIES = [
    'azienda agricola',
    'agricoltore',
    'produttore locale',
    'fattoria',
    'allevamento',
    'vigneto',
    'oliveto'
]

def slugify(text):
    """Convert text to URL-friendly slug"""
    text = re.sub(r'[^\w\s-]', '', text.lower())
    return re.sub(r'[-\s]+', '-', text).strip('-')

def create_unclaimed_profile(place_details, gmaps):
    """
    Crea un profilo non rivendicato da dati Google Maps
    
    Args:
        place_details: Dettagli del place da Google Maps API
        gmaps: Client Google Maps
    """
    app = create_app()
    with app.app_context():
        name = place_details.get('name', 'Azienda Agricola')
        
        # Crea username univoco
        base_username = slugify(name)
        username = base_username
        counter = 1
        while User.query.filter_by(username=username).first():
            username = f"{base_username}-{counter}"
            counter += 1
        
        # Estrai informazioni location
        location = place_details.get('geometry', {}).get('location', {})
        address_components = place_details.get('address_components', [])
        
        city = None
        province = None
        for comp in address_components:
            if 'locality' in comp.get('types', []):
                city = comp.get('long_name')
            elif 'administrative_area_level_2' in comp.get('types', []):
                province = comp.get('long_name')
        
        # Email placeholder
        email = f"{username}@placeholder.ortovicino.it"
        
        # Phone (se disponibile)
        phone = place_details.get('formatted_phone_number', '')
        
        # Descrizione da reviews o types
        description = place_details.get('editorial_summary', {}).get('overview', 
                      f"Azienda agricola locale. Profilo creato automaticamente da dati pubblici. "
                      f"Sei il proprietario? Rivendica questa pagina per gestire i tuoi prodotti.")
        
        # Controlla se esiste già (per phone o coordinate)
        if phone:
            existing = User.query.filter_by(phone=phone, is_farmer=True).first()
            if existing:
                print(f"  ⚠️  Profilo già esistente per {name} (stesso telefono)")
                return None
        
        # Crea user
        user = User(
            username=username,
            email=email,
            company_name=name,
            company_description=description[:500] if description else None,
            phone=phone if phone else None,
            city=city,
            province=province,
            address=place_details.get('formatted_address', ''),
            latitude=location.get('lat'),
            longitude=location.get('lng'),
            is_farmer=True,
            is_scraped=True,
            is_claimed=False,
            claim_token=secrets.token_urlsafe(32),
            data_source='Google Maps API',
            company_slug=username
        )
        
        # Password casuale (non comunicata, user dovrà fare claim)
        user.set_password(secrets.token_urlsafe(24))
        
        try:
            db.session.add(user)
            db.session.commit()
            print(f"  ✓ Creato: {name} ({city}, {province})")
            return user
        except Exception as e:
            db.session.rollback()
            print(f"  ✗ Errore salvando {name}: {e}")
            return None

def search_places_in_province(gmaps, province, query):
    """Cerca places in una provincia specifica"""
    search_query = f"{query} in {province}, Sardegna, Italia"
    
    try:
        places_result = gmaps.places(query=search_query, language='it', region='it')
        return places_result.get('results', [])
    except Exception as e:
        print(f"Errore ricerca '{search_query}': {e}")
        return []

def main():
    """Main scraping function"""
    print("=" * 60)
    print("🌾 ORTOVICINO - GOOGLE MAPS SCRAPER")
    print("=" * 60)
    print(f"📍 Target: {len(TARGET_PROVINCES)} provincie Sardegna")
    print(f"🔍 Query: {len(SEARCH_QUERIES)} tipologie")
    print(f"🔑 API Key: {GOOGLE_MAPS_API_KEY[:8]}...{GOOGLE_MAPS_API_KEY[-4:]}")
    print()
    
    # Inizializza Google Maps client
    gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
    
    total_found = 0
    total_created = 0
    
    for province in TARGET_PROVINCES:
        print(f"\n📍 Provincia: {province}")
        print("-" * 40)
        
        province_count = 0
        
        for query in SEARCH_QUERIES:
            places = search_places_in_province(gmaps, province, query)
            
            if not places:
                continue
            
            print(f"  🔍 '{query}': trovati {len(places)} risultati")
            
            for place in places:
                total_found += 1
                place_id = place.get('place_id')
                
                # Get detailed info
                try:
                    details = gmaps.place(place_id=place_id, language='it')
                    place_details = details.get('result', {})
                    
                    # Filtra solo aziende agricole (verifica types)
                    types = place_details.get('types', [])
                    relevant_types = ['farm', 'food', 'store', 'establishment']
                    if not any(t in types for t in relevant_types):
                        continue
                    
                    # Crea profilo
                    user = create_unclaimed_profile(place_details, gmaps)
                    if user:
                        total_created += 1
                        province_count += 1
                    
                except Exception as e:
                    print(f"  ✗ Errore dettagli place {place_id}: {e}")
                    continue
        
        print(f"  ✅ Totale creati in {province}: {province_count}")
    
    print("\n" + "=" * 60)
    print(f"📊 RISULTATI FINALI")
    print("=" * 60)
    print(f"Trovati: {total_found} places")
    print(f"Creati: {total_created} profili")
    print(f"Duplicati/Errori: {total_found - total_created}")
    print()
    print("✨ I proprietari possono rivendicare i profili su:")
    print("   https://ortovicino.it/rivendica-azienda")
    print()
    print("⚠️  DISCLAIMER GDPR aggiunto al footer del sito")
    print("=" * 60)

if __name__ == '__main__':
    main()
