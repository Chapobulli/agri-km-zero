# Agri KM Zero

Una app per agricoltori e clienti per prodotti agricoli a km0.

## Caratteristiche

- Agricoltori possono pubblicare prodotti (modello freemium).
- Clienti possono cercare agricoltori vicini.
- Messaggistica per acquisti di persona.
- Opzione consegna a domicilio selezionabile dagli agricoltori.
- Pagamenti solo di persona, non gestiti dall'app.

## Installazione Locale

1. Clona il repository.
2. Installa le dipendenze: `pip install -r requirements.txt`
3. Esegui: `python main.py`

## Deploy su Render

1. Crea un account su [Render.com](https://render.com).
2. Collega il tuo repo GitHub.
3. Crea un nuovo **Web Service**:
   - **Runtime**: Python 3.
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT "app:create_app()"`
   - **Environment Variables**:
     - `PYTHON_VERSION`: `3.12`
     - `DATABASE_URL`: (URL del database PostgreSQL)
     - `SECRET_KEY`: (la chiave generata)
4. Aggiungi un database PostgreSQL gratuito su Render e collega via `DATABASE_URL`.
5. Imposta variabili d'ambiente: `SECRET_KEY` (genera una chiave sicura).
6. Deploy!

## Tecnologie

- Backend: Flask
- Database: PostgreSQL (produzione) / SQLite (locale)
- Frontend: HTML, CSS, JavaScript