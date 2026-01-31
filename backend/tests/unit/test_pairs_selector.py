from backend.app.core.pairs_selector import PairsSelector
from backend.app.core.data_fetcher import DataFetcher
import pandas as pd

# Préparation des données
fetcher = DataFetcher()
aapl = fetcher.download_stock("AAPL", "2024-01-01", "2024-06-30")
msft = fetcher.download_stock("MSFT", "2024-01-01", "2024-06-30")
googl = fetcher.download_stock("GOOGL", "2024-01-01", "2024-06-30")

data = pd.DataFrame({
    'AAPL': aapl['Close'],
    'MSFT': msft['Close'],
    'GOOGL': googl['Close']
})

selector = PairsSelector()

# Test 1: Calculer une corrélation
print("--- Test 1 : Calculer une corrélation ---")
matrice_correlation = selector.calculate_correlation(data)
print("Test 1 réussi !")
print(f"Sape: {matrice_correlation}")
print(matrice_correlation)
print(f"\nCorrélation AAPL-MSFT: {matrice_correlation.loc['AAPL', 'MSFT']:.3f}")
print(f"Corrélation AAPL-GOOGL: {matrice_correlation.loc['AAPL', 'GOOGL']:.3f}")

# Test 2 : Tester cointégration
print("\n--- Test 2 : Tester cointégration ---")
aapl_close = aapl['Close']
msft_close = msft['Close']

is_cointegrated, p_value = selector.test_cointegration(aapl_close, msft_close)
print("Test 2 réussi !")
print(f"AAPL-MSFT cointégrée : {is_cointegrated}")
print(f"P-value : {p_value:.4f}")
print(f"Seuil : {selector.pvalue_threshold}")

# Test avec une autre paire
is_cointegrated2, p_value2 = selector.test_cointegration(aapl_close, googl['Close'])
print(f"\nAAPL-GOOGL cointégrée : {is_cointegrated2}")
print(f"P-value : {p_value2:.4f}")

# Test 3 : Trouver toutes les paires
print("\n--- Test 3 : Trouver toutes les paires ---")
tickers = ['AAPL', 'MSFT', 'GOOGL', 'TSLA']
pairs = selector.find_all_pairs(tickers)
print("Test 3 réussi !")
print(f"Nombre de paires générées : {len(pairs)}")
print(f"Paires : {pairs}")

# Test 4 : Filtrer paires valides
print("\n--- Test 4 : Filtrer paires valides ---")

# Création de données de test
test_pairs = [
    ('AAPL', 'MSFT', 0.85, 0.02),   # corr=0.85 >= 0.7 ET p-value=0.02 < 0.05 (acceptée)
    ('AAPL', 'GOOGL', 0.65, 0.03),  # corr=0.65 < 0.7 (rejetée)
    ('MSFT', 'GOOGL', 0.90, 0.15),  # p-value=0.15 > 0.05 (rejetée)
    ('AAPL', 'TSLA', 0.45, 0.01),   # corr=0.45 < 0.7 (rejetée)
]

paires_valides = selector.filter_valid_pairs(test_pairs)
print("Test 4 réussi !")
print(f"Paires testées : {len(test_pairs)}")
print(f"Paires valides : {len(paires_valides)}")
print(f"\nSeuils utilisés :")
print(f" Corrélation minimum : {selector.correlation_threshold}")
print(f" P-value maximum : {selector.pvalue_threshold}")
print(f"\nPaires valides :")
for pair in paires_valides:
    print(f" {pair[0]}-{pair[1]} : corr={pair[2]:.2f}, p-value={pair[3]:.3f}")