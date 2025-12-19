# 🧪 Testing & Debug - Agri KM Zero

## Test Disponibili

### 1. Test Base (test_app.py)
Script Python semplice che non richiede installazioni extra.

**Eseguire:**
```bash
python test_app.py
```

**Testa:**
- ✅ Connessione database
- ✅ Conteggio record per ogni tabella
- ✅ Integrità dati (prodotti orfani, campi mancanti)
- ✅ Tutte le route principali (/, /products, /login, etc.)
- ✅ Profili agricoltori completi
- ✅ Prodotti con associazioni farmer

### 2. Test Pytest (tests/test_basic.py)
Test unitari professionali con pytest.

**Installare:**
```bash
pip install pytest pytest-flask
```

**Eseguire tutti i test:**
```bash
pytest
```

**Eseguire test specifici:**
```bash
pytest tests/test_basic.py::TestPublicPages
pytest tests/test_basic.py::TestPublicPages::test_homepage -v
```

**Test con output dettagliato:**
```bash
pytest -v -s
```

**Testa:**
- ✅ Health check endpoint
- ✅ Pagine pubbliche (homepage, products, login, register)
- ✅ Connessione database
- ✅ Modelli User e Product
- ✅ Workflow agricoltore
- ✅ Integrità dati
- ✅ Endpoint di debug

## 🔍 Endpoint di Debug

### /health
Health check JSON per monitoraggio.

**Risposta:**
```json
{
  "status": "healthy",
  "database": "connected",
  "checks": {
    "users_count": 12,
    "farmers_count": 5,
    "products_count": 23,
    "messages_count": 8
  }
}
```

**Uso:**
```bash
curl http://localhost:5000/health
# O visita nel browser
```

### /debug/users
Tabella HTML di tutti gli utenti con informazioni dettagliate.

**Mostra:**
- ID, Username, Email
- Tipo (Agricoltore/Cliente)
- Località (Provincia, Città)
- Email verificata
- N° prodotti (per agricoltori)
- Data registrazione

### /debug/products
Tabella HTML di tutti i prodotti con dettagli.

**Mostra:**
- ID, Nome, Prezzo
- Unità, Quantità
- Immagine (se presente)
- Agricoltore associato
- Località prodotto
- Categoria, Disponibilità
- Data creazione

### /debug/test-data
JSON diagnostico completo per troubleshooting.

**Risposta:**
```json
{
  "database_tables": {
    "user": 12,
    "product": 23,
    "message": 8
  },
  "sample_users": [...],
  "sample_products": [...],
  "issues": {
    "orphan_products": [],
    "farmers_without_location": [3, 7],
    "products_without_images": [12, 15, 18]
  }
}
```

## 🚀 Come Usare in Produzione

### 1. Monitoring Health Check
Configura un servizio di monitoraggio (UptimeRobot, Pingdom, etc.) per chiamare `/health` ogni 5 minuti.

### 2. Debugging Veloce
Quando c'è un errore:
```bash
# 1. Controlla health check
curl https://your-app.onrender.com/health

# 2. Visita debug pages nel browser
https://your-app.onrender.com/debug/users
https://your-app.onrender.com/debug/products

# 3. Scarica dati diagnostici
curl https://your-app.onrender.com/debug/test-data > debug.json
```

### 3. Test Locali Prima di Deploy
```bash
# Test base
python test_app.py

# Test completi
pytest -v

# Solo test veloci
pytest -m "not slow"
```

## 📊 Interpretare i Risultati

### ✅ Test Passed
Tutto ok, puoi fare deploy.

### ❌ Test Failed
Leggi l'errore:
- **AssertionError**: Condizione non rispettata
- **AttributeError**: Campo mancante
- **ConnectionError**: Database non raggiungibile

### ⚠️ Warnings
Non bloccano il test ma indicano problemi:
- Farmer senza località
- Prodotti orfani
- Campi opzionali vuoti

## 🔧 Troubleshooting

### Test falliscono localmente
```bash
# Verifica database URI
echo $DATABASE_URL

# Verifica app si avvia
python run.py

# Test singolo
pytest tests/test_basic.py::test_health_endpoint -v
```

### Debug endpoint ritornano errore
Controlla che il blueprint sia registrato in `app/__init__.py`:
```python
from .debug import debug as debug_blueprint
app.register_blueprint(debug_blueprint)
```

### Pytest non trova i test
```bash
# Verifica struttura directory
ls tests/
# Deve contenere: __init__.py, test_basic.py

# Verifica pytest.ini esiste
ls pytest.ini
```

## 📝 Best Practices

1. **Prima di ogni commit**: `python test_app.py`
2. **Prima di ogni deploy**: `pytest`
3. **Dopo deploy**: Controlla `/health` endpoint
4. **Settimanalmente**: Rivedi `/debug/test-data` per issues

## 🛡️ Sicurezza

⚠️ **IMPORTANTE**: In produzione, proteggi gli endpoint di debug!

Aggiungi in `app/debug.py`:
```python
@debug.before_request
def restrict_debug():
    # Solo in development o per admin
    if not current_app.debug and not (current_user.is_authenticated and current_user.is_admin):
        abort(403)
```

O disabilita completamente in produzione in `app/__init__.py`:
```python
if app.debug:  # Solo in development
    from .debug import debug as debug_blueprint
    app.register_blueprint(debug_blueprint)
```
