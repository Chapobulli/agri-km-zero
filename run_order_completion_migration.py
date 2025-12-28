"""
Migrazione: Aggiunge campi per il completamento ordini e recensioni
"""
import psycopg2
import os

# Database connection string from environment
db_url = os.environ.get('DATABASE_URL')
if not db_url:
    print("❌ ERROR: DATABASE_URL non impostata nelle variabili d'ambiente")
    exit(1)

print(f"Connessione al database: {db_url.split('@')[1] if '@' in db_url else 'database'}")

try:
    # Connessione al database con SSL
    conn = psycopg2.connect(db_url + "?sslmode=require")
    cursor = conn.cursor()
    
    print("\n📋 Esecuzione migrazione order_completion...")
    
    # Leggi il file SQL
    with open('migrations/add_order_completion.sql', 'r', encoding='utf-8') as f:
        sql = f.read()
    
    # Esegui le query
    cursor.execute(sql)
    
    # Verifica quanti ordini esistono
    cursor.execute("SELECT COUNT(*) FROM order_request")
    total_orders = cursor.fetchone()[0]
    
    print(f"✅ Campi 'completed_at' e 'reviewed' aggiunti con successo")
    print(f"📊 Totale ordini nel database: {total_orders}")
    
    # Commit delle modifiche
    conn.commit()
    print("\n✅ Migrazione completata con successo!")
    
except psycopg2.Error as e:
    print(f"❌ Errore database: {e}")
    if conn:
        conn.rollback()
except FileNotFoundError:
    print("❌ File migrations/add_order_completion.sql non trovato")
except Exception as e:
    print(f"❌ Errore: {e}")
finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
        print("🔌 Connessione chiusa")
