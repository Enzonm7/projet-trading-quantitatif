"""Test de l'installation"""

print("=" * 60)
print("TEST DE L'ENVIRONNEMENT")
print("=" * 60)

packages = {
    'pandas': 'pandas',
    'numpy': 'numpy',
    'yfinance': 'yfinance',
    'matplotlib': 'matplotlib',
    'statsmodels': 'statsmodels',
}

results = []

for display_name, import_name in packages.items():
    try:
        module = __import__(import_name.split('.')[0])
        version = getattr(module, '__version__', 'N/A')
        print(f"{display_name:15} - Version: {version}")
        results.append(True)
    except ImportError as e:
        print(f"{display_name:15} - ERREUR: {e}")
        results.append(False)

print("=" * 60)

if all(results):
    print("SUCCÈS ! Environnement prêt pour le développement.")
else:
    print("Certains packages manquent.")

# Test téléchargement données
print("\nTest de téléchargement...")
try:
    import yfinance as yf
    from datetime import datetime, timedelta
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    data = yf.download('AAPL', 
                      start=start_date.strftime('%Y-%m-%d'), 
                      end=end_date.strftime('%Y-%m-%d'),
                      progress=False)
    
    if len(data) > 0:
        print(f"Téléchargement réussi : {len(data)} jours")
        print("\nAperçu :")
        print(data.head())
    else:
        print("Aucune donnée")
        
except Exception as e:
    print(f"Erreur : {e}")