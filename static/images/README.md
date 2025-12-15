# Guida alle Immagini - Agri KM Zero

## 📁 Struttura delle Cartelle

```
static/images/
├── hero/
│   ├── hero-main.jpg          # Immagine principale hero section (1200x600px)
│   └── hero-bg.jpg            # Sfondo hero section (opzionale)
├── features/
│   ├── fresh-products.jpg     # Icona prodotti freschi (400x300px)
│   ├── sustainability.jpg     # Icona sostenibilità (400x300px)
│   └── direct-connection.jpg  # Icona connessione diretta (400x300px)
├── testimonials/
│   ├── farmer-1.jpg           # Foto agricoltore testimonial (200x200px)
│   ├── customer-1.jpg         # Foto cliente testimonial (200x200px)
│   └── customer-2.jpg         # Foto cliente testimonial (200x200px)
├── products/
│   ├── vegetables.jpg         # Categoria ortaggi (300x300px)
│   ├── fruits.jpg             # Categoria frutta (300x300px)
│   ├── dairy.jpg              # Categoria latticini (300x300px)
│   └── default-product.jpg    # Immagine di default per prodotti
└── logo/
    ├── logo.png               # Logo principale (200x80px, PNG trasparente)
    └── favicon.ico            # Favicon (32x32px, ICO)
```

## 🔗 Come Referenziare le Immagini nei Template

Usa la funzione Flask `url_for()` per referenziare le immagini statiche:

```html
<!-- Logo nella navbar -->
<img src="{{ url_for('static', filename='images/logo/logo.png') }}" alt="Logo">

<!-- Immagine hero -->
<img src="{{ url_for('static', filename='images/hero/hero-main.jpg') }}" alt="Prodotti Locali">

<!-- Immagine con fallback -->
<img src="{{ url_for('static', filename='images/features/fresh-products.jpg') }}"
     alt="Prodotti Freschi"
     onerror="this.src='https://via.placeholder.com/400x300/4CAF50/ffffff?text=Immagine+Non+Trovata'">
```

## 📐 Dimensioni e Formati Consigliati

| Tipo Immagine | Dimensioni | Formato | Note |
|---------------|------------|---------|------|
| Logo | 200x80px | PNG | Sfondo trasparente |
| Hero | 1200x600px | JPG | Alta qualità, compresso |
| Features | 400x300px | JPG/PNG | Buona qualità |
| Testimonials | 200x200px | JPG | Foto persone |
| Products | 300x300px | JPG | Prodotti alimentari |
| Favicon | 32x32px | ICO | Icona browser |

## 🛠️ Ottimizzazione Immagini

1. **Compressione**: Usa strumenti come TinyPNG o ImageOptim
2. **Formati Moderni**: WebP per browser moderni, JPG per compatibilità
3. **Nomi File**: Usa minuscolo, trattini, descrittivi (es: `hero-prodotti-freschi.jpg`)
4. **Alt Text**: Sempre includi testo alternativo per accessibilità

## 📤 Come Aggiungere Immagini

1. Prepara le immagini nelle dimensioni corrette
2. Comprimi per il web
3. Carica nella cartella appropriata
4. Aggiorna i template HTML se necessario
5. Testa localmente e su produzione

## 🔄 Aggiornamenti Automatici

Quando aggiungi nuove immagini:
- Flask rileva automaticamente i file in `static/`
- Nessun riavvio server necessario
- Le modifiche sono immediate in sviluppo
- Su Render: push su GitHub per deploy automatico