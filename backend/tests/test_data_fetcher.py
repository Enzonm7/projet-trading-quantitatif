from backend.app.core.data_fetcher import DataFetcher

# Test 1 : Téléchargement réussi
fetcher = DataFetcher()
data = fetcher.download_stock("AAPL", "2024-01-01", "2024-01-31")
print("Test 1 réussi !")
print(f"Shape: {data.shape}")
print(data.head())

# Test 2 : Téléchargement échoué
try:
    data_invalid = fetcher.download_stock("TICKERINVALIDE123", "2024-01-01", "2024-01-31")
    print("Test 2 échoué : lève une erreur")
except ValueError as e:
    print(f"Test 2 réussi : {e}")

# Test 3 : Download pair
print("\n--- Test download_pair ---")
pair_data = fetcher.download_pair("AAPL", "MSFT", "2024-01-01", "2024-01-31")
print("Test 3 réussi !")
print(f"Shape: {pair_data.shape}")
print(pair_data.head())
print(f"Colonnes: {list(pair_data.columns)}")

# Test 4 : Cache - Téléchargement
print("\n--- Test 4 : Cache (téléchargeent) ---")
import time
start = time.time()
data1 = fetcher.get_cached_data("GOOGL", "2024-01-01", "2024-01-31")
temps1 = time.time() - start
print(f"Téléchargement : {temps1:.2f}s")
print(f"Shape: {data1.shape}")

# Test 5 : Cache - Depuis cache
print("\n--- Test 5 : Cache (depuis cache) ---")
start = time.time()
data2 = fetcher.get_cached_data("GOOGL", "2024-01-01", "2024-01-31")
temps2 = time.time() - start
print(f"Depuis le cache : {temps2:.2f}s")
print(f"Le cache est-il plus rapide ? {temps2 < temps1}")
print(f"Les données sont-elles identiques ? {data1.equals(data2)}")