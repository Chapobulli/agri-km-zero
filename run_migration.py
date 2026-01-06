"""Execute SQL migration on Render database"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection from env var only (no hardcoded secrets)
db_url = os.environ.get("DATABASE_URL")
if not db_url:
    raise RuntimeError("DATABASE_URL non impostata. Imposta la variabile d'ambiente e riprova.")

print(f"Connecting to database...")

try:
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    
    print("✓ Connected to database")
    
    # Add minimum_order_quantity column
    print("\n1. Adding minimum_order_quantity column to product table...")
    cursor.execute("""
        ALTER TABLE product ADD COLUMN IF NOT EXISTS minimum_order_quantity INTEGER DEFAULT 1;
    """)
    print("✓ Column added")
    
    # Update existing products
    print("\n2. Updating existing products with minimum order quantity of 10...")
    cursor.execute("""
        UPDATE product SET minimum_order_quantity = 10 
        WHERE minimum_order_quantity IS NULL OR minimum_order_quantity < 10;
    """)
    updated = cursor.rowcount
    print(f"✓ Updated {updated} products")
    
    # Create review table
    print("\n3. Creating review table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS review (
            id SERIAL PRIMARY KEY,
            farmer_id INTEGER NOT NULL REFERENCES "user"(id),
            client_id INTEGER REFERENCES "user"(id),
            order_id INTEGER REFERENCES order_request(id),
            client_name VARCHAR(150),
            rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    print("✓ Table created")
    
    # Create indexes
    print("\n4. Creating indexes...")
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_review_farmer_id ON review(farmer_id);
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_review_client_id ON review(client_id);
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_review_order_id ON review(order_id);
    """)
    print("✓ Indexes created")

    # Add order completion fields
    print("\n5. Adding order completion fields...")
    cursor.execute("""
        ALTER TABLE order_request ADD COLUMN IF NOT EXISTS completed_at TIMESTAMP;
    """)
    cursor.execute("""
        ALTER TABLE order_request ADD COLUMN IF NOT EXISTS reviewed BOOLEAN DEFAULT FALSE;
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_order_request_completed ON order_request(completed_at);
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_order_request_reviewed ON order_request(reviewed);
    """)
    print("✓ Order completion columns added")
    
    # Commit changes
    conn.commit()
    print("\n✅ Migration completed successfully!")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    if 'conn' in locals():
        conn.rollback()
