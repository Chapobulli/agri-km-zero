"""
Script da eseguire su Render per caricare aziende
Comando: python load_companies.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Esegui lo script di scraping
from scripts.scrape_openstreetmap import main

if __name__ == '__main__':
    print("Caricamento aziende da OpenStreetMap...")
    main()
