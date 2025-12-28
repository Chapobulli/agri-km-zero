# Sistema di Scraping e Claim Business - OrtoVicino

## 📋 Overview

Sistema completo per importare aziende agricole da fonti pubbliche e permettere ai proprietari di rivendicare i loro profili.

## 🎯 Funzionalità

1. **Scraping Automatico** - Import da OpenStreetMap (GRATUITO) o Google Maps API
2. **Profili "Unclaimed"** - Aziende visibili ma non gestibili fino al claim
3. **Sistema di Rivendicazione** - Proprietari possono rivendicare via email
4. **Badge Verifica** - Distintivi "Verificato" / "Non Verificato" sui profili
5. **GDPR Compliant** - Disclaimer e possibilità di rimozione dati

## 🚀 Setup - OPZIONE 1: OpenStreetMap (CONSIGLIATO - GRATUITO)

### 1. Installare Dipendenze

```bash
pip install requests geopy
```

### 2. Eseguire lo Scraping

```bash
python scripts/scrape_openstreetmap.py
```

**Vantaggi**:
- ✅ 100% GRATUITO (no billing account)
- ✅ No API key necessaria
- ✅ Open Source (ODbL License)
- ✅ Nessun rate limit severo
- ✅ Dati pubblici collaborativi

**Come funziona**:
- Usa Overpass API per interrogare OpenStreetMap
- Cerca POI con tag: `landuse=farmland`, `amenity=farm`, `shop=farm`, etc.
- Bounding box: Sardegna (lat 38.8-41.3, lon 8.1-9.9)
- Reverse geocoding con Nominatim per città/provincia

## 🚀 Setup - OPZIONE 2: Google Maps API (Richiede Billing)

### 1. Installare Dipendenze

```bash
pip install googlemaps
```

### 2. Ottenere API Key Google Maps

1. Vai su [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuovo progetto o selezionane uno esistente
3. Abilita **Places API**
4. Crea credenziali (API Key)
5. Imposta restrizioni (opzionale ma raccomandato):
   - Restrizioni HTTP referrer per production
   - Limita alle API necessarie (Places API)

### 3. Configurare Variabile d'Ambiente

```bash
# Windows PowerShell
$env:GOOGLE_MAPS_API_KEY="YOUR_API_KEY_HERE"

# Windows CMD
set GOOGLE_MAPS_API_KEY=YOUR_API_KEY_HERE

# Linux/Mac
export GOOGLE_MAPS_API_KEY="YOUR_API_KEY_HERE"
```

O aggiungi al file `.env`:
```
GOOGLE_MAPS_API_KEY=your_key_here
```

### 4. Eseguire lo Scraping

```bash
python scripts/scrape_google_maps.py
```

## 📊 Confronto Soluzioni

| Caratteristica | OpenStreetMap | Google Maps API |
|---|---|---|
| **Costo** | ✅ GRATUITO | ❌ $11.90 per 700 aziende |
| **Setup** | ✅ Nessuna API key | ❌ Richiede billing account |
| **Qualità Dati** | ⚠️ Variabile (crowd-sourced) | ✅ Alta (commerciale) |
| **Copertura** | ⚠️ Dipende da contributi | ✅ Completa |
| **Rate Limits** | ✅ Gentili | ⚠️ Severi |
| **License** | ✅ ODbL (open) | ⚠️ Proprietaria |

**Raccomandazione**: Inizia con **OpenStreetMap** (gratuito), poi integra con Google Maps se necessario.

## 📊 Funzionamento

### Scraping Process (OSM)

1. **Query Overpass**: Interroga OSM con bounding box Sardegna
2. **Tag filtering**: Cerca `landuse=farmland`, `amenity=farm`, `shop=farm`, etc.
3. **Reverse geocoding**: Nominatim per città/provincia se mancante
4. **Deduplicazione**: Verifica telefono e coordinate duplicate
5. **Creazione profilo**: User con `is_scraped=True`, `data_source='OpenStreetMap'`

### Scraping Process (Google Maps)

1. **Ricerca per provincia**: Scandisce 5 provincie Sardegna
2. **Query multiple**: 7 tipologie (azienda agricola, produttore locale, etc.)
3. **Filtro types**: Verifica che siano effettivamente farm/food
4. **Estrazione dati**: Nome, indirizzo, telefono, coordinate
5. **Creazione profilo**: User con `is_scraped=True`, `is_claimed=False`

### Claim Process

1. Utente cerca azienda su `/rivendica-azienda`
2. Clicca "Rivendica" sul profilo trovato
3. Inserisce email e telefono per verifica
4. Sistema invia link di verifica (TODO: email service)
5. Click su link verifica → `is_claimed=True`
6. Redirect a reset password per impostare credenziali

## 🔒 Compliance Legale

### Google Maps Terms of Service

✅ **Permesso**: Usare dati per creare servizi derivati
✅ **Attribution**: Footer include crediti OpenStreetMap
✅ **Rate Limits**: Rispettati (max 100 place details/minuto)
❌ **NON permesso**: Redistribuire dati raw, cachare >30 giorni

### GDPR (Art. 14)

✅ **Fonte pubblica**: Dati da Google Maps (fonte pubblica)
✅ **Trasparenza**: Disclaimer in footer
✅ **Diritto accesso**: Link "rivendica" prominente
✅ **Diritto cancellazione**: Email privacy@ortovicino.it

## 🎨 UI Features

### Badge sui Profili

```html
<!-- Profilo Verificato -->
<span class="badge badge-success">
    <i class="fas fa-check-circle"></i> Verificato
</span>

<!-- Profilo Non Verificato -->
<span class="badge badge-warning">
    <i class="fas fa-exclamation-triangle"></i> Non Verificato
</span>
```

### Banner Claim

Profili unclaimed mostrano banner prominente:
> "Sei il proprietario? Rivendica questo profilo per gestire prodotti e ordini"

## 📁 Struttura Database

### Nuovi Campi `User`

```python
is_claimed = db.Column(db.Boolean, default=False)
is_scraped = db.Column(db.Boolean, default=False)  
claim_token = db.Column(db.String(64), unique=True)
verified_at = db.Column(db.DateTime)
data_source = db.Column(db.String(100))  # "Google Maps API", "Manual", "Claimed"
```

## 🛣️ Routes

- `GET /rivendica-azienda` - Pagina ricerca azienda
- `GET /rivendica/<username>` - Form rivendicazione specifica
- `POST /rivendica/<username>` - Invia richiesta verifica
- `GET /verify-claim/<token>` - Verifica claim via email

## 📧 TODO: Email Service

Per produzione, implementare invio email:

```python
def send_claim_verification_email(company, contact_email):
    verify_url = url_for('main.verify_claim', 
                        token=company.claim_token, 
                        _external=True)
    
    # Usa SendGrid, AWS SES, o altro servizio
    send_email(
        to=contact_email,
        subject=f"Verifica proprietà {company.company_name}",
        body=f"Clicca per verificare: {verify_url}"
    )
```

## 🔍 Monitoraggio

Controlla profili creati:

```sql
-- Profili scraped non claimed
SELECT company_name, city, data_source, claim_token
FROM "user"
WHERE is_scraped = TRUE AND is_claimed = FALSE;

-- Profili verificati
SELECT company_name, verified_at
FROM "user"
WHERE is_claimed = TRUE
ORDER BY verified_at DESC;
```

## ⚠️ Rate Limits Google Maps

**Free Tier**: $200/mese credito gratuito

- **Places Search**: $0.032 per richiesta
- **Place Details**: $0.017 per richiesta

Esempio costi:
- 5 provincie × 7 query × 20 results = 700 places
- 700 details = 700 × $0.017 = **$11.90**
- Rientra nel free tier

## 🔄 Aggiornamenti Futuri

- [ ] Scraping periodico (cron job)
- [ ] Import da altre fonti (Pagine Gialle, CCIAA)
- [ ] Verifica automatica via SMS
- [ ] Dashboard admin per approvazioni manuali
- [ ] Analytics su claims (tasso conversione)

## 📞 Supporto

Per domande o problemi:
- Email: info@ortovicino.it
- GitHub Issues: [link al repo]
