-- Aggiunge i campi per il completamento ordini e le recensioni
-- completed_at: timestamp quando l'ordine viene completato dall'agricoltore
-- reviewed: flag per sapere se l'ordine è stato recensito

ALTER TABLE order_request 
ADD COLUMN IF NOT EXISTS completed_at TIMESTAMP;

ALTER TABLE order_request 
ADD COLUMN IF NOT EXISTS reviewed BOOLEAN DEFAULT FALSE;

-- Crea un indice per velocizzare le query sugli ordini completati
CREATE INDEX IF NOT EXISTS idx_order_request_completed ON order_request(completed_at);
CREATE INDEX IF NOT EXISTS idx_order_request_reviewed ON order_request(reviewed);
