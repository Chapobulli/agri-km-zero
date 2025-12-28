"""
Script per importare aziende agricole da OpenStreetMap (GRATUITO)
Uso: python scripts/scrape_openstreetmap.py

VANTAGGI:
- 100% GRATUITO (no billing, no API key)
- Open Source e conforme GDPR
- Dati pubblici collaborativi
- Nessun rate limit severo

REQUISITI:
- pip install requests geopy
- Connessione internet

OpenStreetMap License:
- ODbL (Open Database License) - dati pubblici
- Attribution richiesta (già nel footer)
- Permesso uso commerciale con attribuzione
"""

import os
import sys
import secrets
import re
import time
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    import requests
    from geopy.geocoders import Nominatim
except ImportError:
    print("ERROR: Installa le dipendenze con: pip install requests geopy")
    sys.exit(1)

from app import create_app, db
from app.models import User

# Configurazione
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
USER_AGENT = "OrtoVicino/1.0 (contact@ortovicino.it)"  # Identifica la tua app

# Bounding box Sardegna
SARDEGNA_BBOX = {
    'south': 38.8,   # Lat minima
    'north': 41.3,   # Lat massima
    'west': 8.1,     # Lon minima
    'east': 9.9      # Lon massima
}

# Tag OSM per aziende agricole (solo aziende agricole vere)
FARM_TAGS = [
    'shop=farm',              # Vendita diretta azienda agricola
    'shop=greengrocer',       # Fruttivendolo
    'landuse=farmland',       # Terreno agricolo con edifici
    'landuse=vineyard',       # Vigneto
    'amenity=farm',           # Fattoria
    'craft=winery',           # Cantina vinicola
    'office=agricultural',    # Ufficio azienda agricola
    'tourism=farm'            # Agriturismo/fattoria didattica
]

def slugify(text):
    """Convert text to URL-friendly slug"""
    text = re.sub(r'[^\w\s-]', '', text.lower())
    return re.sub(r'[-\s]+', '-', text).strip('-')

def build_overpass_query(bbox, tags):
    """
    Costruisce query Overpass QL per trovare farm/agricultural POI
    Documentazione: https://wiki.openstreetmap.org/wiki/Overpass_API
    """
    # Union di tutte le query per i vari tag
    tag_queries = []
    for tag in tags:
        key, value = tag.split('=')
        # Cerca nodi (points)
        tag_queries.append(f'node["{key}"="{value}"]({bbox["south"]},{bbox["west"]},{bbox["north"]},{bbox["east"]})')
        # Cerca way (areas/buildings)
        tag_queries.append(f'way["{key}"="{value}"]({bbox["south"]},{bbox["west"]},{bbox["north"]},{bbox["east"]})')
    
    query = f"""
    [out:json][timeout:90];
    (
      {';'.join(tag_queries)};
    );
    out center tags;
    """
    return query

def query_overpass(query):
    """Esegue query su Overpass API"""
    try:
        print(f"  🔍 Interrogando Overpass API...")
        response = requests.post(
            OVERPASS_URL,
            data={'data': query},
            headers={'User-Agent': USER_AGENT},
            timeout=120
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"  ✗ Errore Overpass API: {e}")
        return None

def extract_location_info(tags):
    """Estrae città e provincia dai tags OSM"""
    city = tags.get('addr:city') or tags.get('addr:town') or tags.get('addr:village')
    province = tags.get('addr:province') or tags.get('addr:state')
    
    # Se non ci sono tag addr, prova altri
    if not city:
        city = tags.get('place')
    
    return city, province

def geocode_reverse(lat, lng):
    """Ottiene città/provincia da coordinate usando Nominatim"""
    try:
        geolocator = Nominatim(user_agent=USER_AGENT)
        location = geolocator.reverse(f"{lat}, {lng}", language='it')
        
        if location and location.raw.get('address'):
            addr = location.raw['address']
            city = (addr.get('city') or addr.get('town') or 
                   addr.get('village') or addr.get('municipality'))
            province = addr.get('province') or addr.get('county')
            return city, province, location.address
    except Exception as e:
        print(f"    ⚠️  Geocoding error: {e}")
    
    return None, None, None

def create_profile_from_osm(element):
    """Crea profilo da elemento OSM"""
    app = create_app()
    with app.app_context():
        tags = element.get('tags', {})
        
        # Estrai nome
        name = (tags.get('name') or tags.get('operator') or 
                tags.get('brand') or 'Azienda Agricola')
        
        if not name or name == 'Azienda Agricola':
            return None  # Skip senza nome
        
        # Coordinate (usa 'center' per way, diretto per node)
        if 'center' in element:
            lat = element['center']['lat']
            lng = element['center']['lon']
        else:
            lat = element.get('lat')
            lng = element.get('lon')
        
        if not lat or not lng:
            return None
        
        # Estrai location
        city, province = extract_location_info(tags)
        
        # Se mancano, usa reverse geocoding
        if not city or not province:
            city_geo, prov_geo, full_address = geocode_reverse(lat, lng)
            city = city or city_geo
            province = province or prov_geo
            time.sleep(1)  # Rate limit Nominatim (1 req/sec)
        else:
            full_address = f"{name}, {city}" if city else name
        
        # Filtra solo Sardegna
        if province and province not in ['Cagliari', 'Sassari', 'Oristano', 'Nuoro', 'Sud Sardegna', 'Carbonia-Iglesias', 'Medio Campidano', 'Ogliastra', 'Olbia-Tempio']:
            return None
        
        # Username univoco
        base_username = slugify(name)
        username = base_username
        counter = 1
        while User.query.filter_by(username=username).first():
            username = f"{base_username}-{counter}"
            counter += 1
        
        # Email placeholder
        email = f"{username}@placeholder.ortovicino.it"
        
        # Phone da OSM
        phone = tags.get('phone') or tags.get('contact:phone')
        
        # Website
        website = tags.get('website') or tags.get('contact:website')
        
        # Description
        description = (tags.get('description') or 
                      f"Azienda agricola locale. Profilo creato automaticamente da dati OpenStreetMap. "
                      f"Sei il proprietario? Rivendica questa pagina.")
        
        # Controlla duplicati (stesso telefono o coordinate molto vicine)
        if phone:
            existing = User.query.filter_by(phone=phone, is_farmer=True).first()
            if existing:
                print(f"  ⚠️  Duplicato (telefono): {name}")
                return None
        
        # Controlla coordinate duplicate (entro 50m)
        nearby = User.query.filter(
            User.is_farmer == True,
            User.latitude.isnot(None),
            db.func.abs(User.latitude - lat) < 0.001,  # ~100m
            db.func.abs(User.longitude - lng) < 0.001
        ).first()
        
        if nearby:
            print(f"  ⚠️  Duplicato (coordinate): {name}")
            return None
        
        # Crea user
        user = User(
            username=username,
            email=email,
            company_name=name,
            company_description=description[:500] if description else None,
            phone=phone,
            city=city,
            province=province,
            address=full_address,
            latitude=lat,
            longitude=lng,
            is_farmer=True,
            is_scraped=True,
            is_claimed=False,
            claim_token=secrets.token_urlsafe(32),
            data_source='OpenStreetMap',
            company_slug=username
        )
        
        # Password casuale
        user.set_password(secrets.token_urlsafe(24))
        
        try:
            db.session.add(user)
            db.session.commit()
            print(f"  ✓ {name} ({city or 'N/A'}, {province or 'N/A'})")
            return user
        except Exception as e:
            db.session.rollback()
            print(f"  ✗ Errore: {name} - {e}")
            return None

def main():
    """Main scraping function"""
    print("=" * 60)
    print("🌾 ORTOVICINO - OPENSTREETMAP SCRAPER")
    print("=" * 60)
    print(f"📍 Area: Sardegna")
    print(f"🔍 Tag OSM: {len(FARM_TAGS)} tipologie")
    print(f"💰 Costo: GRATUITO (OpenStreetMap)")
    print(f"🎯 Limite: 10 aziende per test")
    print()
    
    # Costruisci e esegui query
    query = build_overpass_query(SARDEGNA_BBOX, FARM_TAGS)
    
    print("⏳ Interrogazione Overpass API (può richiedere 30-60 sec)...")
    result = query_overpass(query)
    
    if not result or 'elements' not in result:
        print("❌ Nessun risultato dalla query")
        return
    
    elements = result['elements']
    print(f"✅ Trovati {len(elements)} elementi OSM")
    print(f"🎯 Creazione limitata a 10 aziende per test")
    print()
    
    # LIMITE: Max 10 aziende per iniziare
    MAX_COMPANIES = 10
    
    total_created = 0
    total_skipped = 0
    
    print("📥 Creazione profili...")
    print("-" * 60)
    
    for idx, element in enumerate(elements, 1):
        # Stop dopo aver creato 10 aziende
        if total_created >= MAX_COMPANIES:
            print(f"\n✋ Raggiunto limite di {MAX_COMPANIES} aziende")
            break
            
        if idx % 10 == 0:
            print(f"  Progresso: {idx}/{len(elements)}...")
        
        user = create_profile_from_osm(element)
        if user:
            total_created += 1
        else:
            total_skipped += 1
        
        # Rate limit gentile
        time.sleep(0.5)
    
    print()
    print("=" * 60)
    print(f"📊 RISULTATI FINALI")
    print("=" * 60)
    print(f"Elementi OSM: {len(elements)}")
    print(f"Profili creati: {total_created}")
    print(f"Saltati/Duplicati: {total_skipped}")
    print()
    print("✨ I proprietari possono rivendicare i profili su:")
    print("   https://ortovicino.it/rivendica-azienda")
    print()
    print("📜 OpenStreetMap © OpenStreetMap contributors")
    print("   License: ODbL (Open Database License)")
    print("=" * 60)

if __name__ == '__main__':
    main()
