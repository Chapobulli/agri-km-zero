-- Migration: Add minimum_order_quantity to products and create review table

-- Add minimum_order_quantity column to product table
ALTER TABLE product ADD COLUMN IF NOT EXISTS minimum_order_quantity INTEGER DEFAULT 1;

-- Update existing products to have minimum order quantity of 10
UPDATE product SET minimum_order_quantity = 10 WHERE minimum_order_quantity IS NULL OR minimum_order_quantity < 10;

-- Create review table
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

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_review_farmer_id ON review(farmer_id);
CREATE INDEX IF NOT EXISTS idx_review_client_id ON review(client_id);
CREATE INDEX IF NOT EXISTS idx_review_order_id ON review(order_id);
