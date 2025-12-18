# Province e comuni della Sardegna
SARDEGNA_LOCATIONS = {
    "Cagliari": ["Cagliari", "Quartu Sant'Elena", "Assemini", "Capoterra", "Selargius", "Sestu", "Monserrato", 
                 "Decimomannu", "Elmas", "Maracalagonis", "Quartucciu", "Sarroch", "Sinnai", "Uta", "Villa San Pietro",
                 "Pula", "Domus de Maria", "Teulada", "Santadi", "Villaputzu", "Muravera", "San Vito", "Castiadas"],
    
    "Nuoro": ["Nuoro", "Siniscola", "Macomer", "Orosei", "Dorgali", "Tortolì", "Bitti", "Onifai", "Oliena", "Orgosolo",
              "Posada", "Borore", "Birori", "Bolotana", "Bortigali", "Dualchi", "Lei", "Macomer", "Noragugume", "Silanus",
              "Fonni", "Gavoi", "Mamoiada", "Ollolai", "Oniferi", "Orani", "Orotelli", "Ottana", "Sarule", "Teti", "Tiana"],
    
    "Oristano": ["Oristano", "Terralba", "Cabras", "Bosa", "Ghilarza", "Cuglieri", "Marrubiu", "Ales", "Arborea", "Baratili San Pietro",
                 "Milis", "Narbolia", "Nurachi", "Riola Sardo", "San Vero Milis", "Santa Giusta", "Simaxis", "Solarussa", "Tramatza",
                 "Zeddiani", "Fordongianus", "Seneghe", "Scano di Montiferro", "Tresnuraghes", "Flussio", "Magomadas", "Modolo", "Sagama",
                 "Paulilatino", "Bonarcado", "Santu Lussurgiu", "Seneghe", "Abbasanta", "Aidomaggiore", "Norbello", "Sedilo", "Sorradile",
                 "Allai", "Assolo", "Baradili", "Baressa", "Curcuris", "Gonnosnò", "Gonnoscodina", "Gonnostramatza", "Masullas", "Mogoro",
                 "Morgongiori", "Pompu", "Ruinas", "Simala", "Siris", "Uras", "Usellus", "Villa Sant'Antonio", "Villa Verde"],
    
    "Sassari": ["Sassari", "Alghero", "Olbia", "Porto Torres", "Tempio Pausania", "Arzachena", "La Maddalena", "Sorso", "Sennori",
                "Castelsardo", "Ozieri", "Thiesi", "Bonorva", "Ittiri", "Uri", "Usini", "Ossi", "Tissi", "Muros", "Cargeghe",
                "Codrongianos", "Florinas", "Olmedo", "Putifigari", "Villanova Monteleone", "Monteleone Rocca Doria", "Romana",
                "Padria", "Mara", "Pozzomaggiore", "Semestene", "Bessude", "Borutta", "Cheremule", "Giave", "Torralba", "Bonnanaro",
                "Santa Maria Coghinas", "Valledoria", "Viddalba", "Badesi", "Trinità d'Agultu e Vignola", "Aggius", "Aglientu",
                "Luogosanto", "Luras", "Calangianus", "Telti", "Loiri Porto San Paolo", "Golfo Aranci", "Palau", "Sant'Antonio di Gallura",
                "Bortigiadas", "Monti", "Padru", "Berchidda", "Oschiri", "Tula", "Erula", "Perfugas", "Laerru", "Martis", "Nulvi",
                "Chiaramonti", "Sedini", "Bulzi", "Tergu", "Ploaghe", "Ardara", "Mores", "Siligo", "Banari", "Ittireddu"],
    
    "Sud Sardegna": ["Carbonia", "Iglesias", "Gonnesa", "Portoscuso", "Sant'Antioco", "Carloforte", "Calasetta", "Villamassargia",
                     "Domusnovas", "Musei", "Buggerru", "Fluminimaggiore", "Arbus", "Guspini", "Villacidro", "San Gavino Monreale",
                     "Sardara", "Sanluri", "Samassi", "Serramanna", "Serrenti", "Villasor", "Decimoputzu", "Siliqua", "Vallermosa",
                     "Villaspeciosa", "Narcao", "Perdaxius", "Santadi", "Tratalias", "Villaperuccio", "Masainas", "Piscinas", "Giba",
                     "San Giovanni Suergiu", "Nuxis", "Teulada", "Domus de Maria", "Pula", "Villa San Pietro", "Sarroch", "Capoterra"]
}

def get_provinces():
    """Ritorna lista ordinata di province sarde"""
    return sorted(SARDEGNA_LOCATIONS.keys())

def get_cities(province):
    """Ritorna lista comuni per provincia sarda"""
    return sorted(SARDEGNA_LOCATIONS.get(province, []))
