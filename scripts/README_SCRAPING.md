# Sistema di Scraping e Claim Business - OrtoVicino

## 📋 Overview

Sistema completo per importare aziende agricole da OpenStreetMap (fonte pubblica e gratuita) e permettere ai proprietari di rivendicare i loro profili.

## 🎯 Funzionalità

1. **Scraping Automatico** - Import gratuito da OpenStreetMap
2. **Profili "Unclaimed"** - Aziende visibili ma non gestibili fino al claim
3. **Sistema di Rivendicazione** - Proprietari possono rivendicare via email
4. **Badge Verifica** - Distintivi "Verificato" / "Non Verificato" sui profili
5. **GDPR Compliant** - Disclaimer e possibilità di rimozione dati

## 🚀 Setup

### 1. Installare Dipendenze

```bash
pip install requests geopy
```

### 2. Eseguire lo Scraping

```bash
python scripts/scrape_openstreetmap.py
```

**Vantaggi OpenStreetMap**:
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

## 📊 Funzionamento

### Scraping Process

1. **Query Overpass**: Interroga OSM con bounding box Sardegna
2. **Tag filtering**: Cerca `landuse=farmland`, `amenity=farm`, `shop=farm`, etc.
3. **Reverse geocoding**: Nominatim per città/provincia se mancante
4. **Deduplicazione**: Verifica telefono e coordinate duplicate
5. **Creazione profilo**: User con `is_scraped=True`, `data_source='OpenStreetMap'`

### Claim Process

1. Utente cerca azienda su `/rivendica-azienda`
2. Clicca "Rivendica" sul profilo trovato
3. Inserisce email e telefono per verifica
4. Sistema invia link di verifica (TODO: email service)
5. Click su link verifica → `is_claimed=True`
6. Redirect a reset password per impostare credenziali

## 🔒 Compliance Legale

### OpenStreetMap License (ODbL)

✅ **Uso libero**: Dati utilizzabili per qualsiasi scopo
✅ **Attribution**: Footer include crediti © OpenStreetMap contributors
✅ **Share-Alike**: Modifiche ai dati OSM devono essere condivise
✅ **No API restrictions**: Nessun limite commerciale

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
