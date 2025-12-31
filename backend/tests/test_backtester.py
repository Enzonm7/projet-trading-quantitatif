from backend.app.core.data_fetcher import DataFetcher
from backend.app.core.pairs_selector import PairsSelector
from backend.app.core.backtester import Backtester
from scipy import stats

# Initialisation des modules
fetcher = DataFetcher()
selector = PairsSelector(correlation_threshold=0.7, pvalue_threshold=0.05)
backtester = Backtester(capital_initial=10000.0, seuil_entree=2.0, seuil_sortie=0.5)

# Téléchargement des données pour une paire (AAPL-MSFT)
print("\n--- Téléchargement des données ---")
pair_data = fetcher.download_pair("AAPL", "MSFT", "2023-01-01", "2024-01-01")
print(f"Données téléchargées : {pair_data.shape}")
print(f"Colonnes : {list(pair_data.columns)}")

# Extraction des prix de clôture
prix_aapl = pair_data['Close_AAPL']
prix_msft = pair_data['Close_MSFT']

# Calcul du ratio de couverture (hedge ratio) avec PairsSelector
print("\n--- Calcul du ratio de couverture ---")
slope, intercept = stats.linregress(prix_msft, prix_aapl)[:2]
ratio_couverture = slope
print(f"Ratio de couverture (hedge ratio) : {ratio_couverture:.4f}")
print(f"Intercept : {intercept:.4f}")

# Test de cointégration pour validation
is_cointegrated, p_value = selector.test_cointegration(prix_aapl, prix_msft)
print(f"Paire cointégrée ? {is_cointegrated} (p-value: {p_value:.4f})")


# Test 1 : Calcul du spread
print("\n--- Test 1 : Calcul du spread ---")

try:
    spread = backtester.calculer_spread(prix_aapl, prix_msft, ratio_couverture)
    print("Test 1 réussi !")
    print(f"  Shape du spread : {spread.shape}")
    print(f"  Moyenne du spread : {spread.mean():.4f}")
    print(f"  Écart-type du spread : {spread.std():.4f}")
    print(f"  Premières valeurs :")
    print(spread.head())
except Exception as e:
    print(f"Test 1 échoué : {e}")


# Test 2 : Calcul du z-score
print("\n--- Test 2 : Calcul du z-score ---")

try:
    zscore = backtester.calculer_zscore(spread, window=20)
    print("Test 2 réussi !")
    print(f"  Shape du z-score : {zscore.shape}")
    print(f"  Moyenne du z-score : {zscore.mean():.4f}")
    print(f"  Écart-type du z-score : {zscore.std():.4f}")
    print(f"  Min/Max : {zscore.min():.4f} / {zscore.max():.4f}")
    print(f"  Premières valeurs (après warmup) :")
    print(zscore.iloc[20:25])
except Exception as e:
    print(f"Test 2 échoué : {e}")


# Test 3 : Génération des signaux
print("\n--- Test 3 : Génération des signaux ---")

try:
    df_signaux = backtester.generer_signaux(zscore)
    print("Test 3 réussi !")
    print(f"  Shape des signaux : {df_signaux.shape}")
    print(f"  Colonnes : {list(df_signaux.columns)}")
    
    # Statistiques sur les signaux
    nb_long = (df_signaux['signal'] == 1).sum()
    nb_short = (df_signaux['signal'] == -1).sum()
    nb_neutre = (df_signaux['signal'] == 0).sum()
    
    print(f"  Signaux LONG : {nb_long}")
    print(f"  Signaux SHORT : {nb_short}")
    print(f"  Signaux NEUTRE : {nb_neutre}")
    print(f"  Échantillon de signaux :")
    print(df_signaux[['zscore', 'signal', 'position']].iloc[20:30])
except Exception as e:
    print(f"Test 3 échoué : {e}")


# Test 4 : Simulation des trades
print("\n--- Test 4 : Simulation des trades ---")

try:
    df_trades = backtester.simuler_trades(df_signaux, prix_aapl, prix_msft, ratio_couverture)
    print("Test 4 réussi !")
    print(f"  Shape des trades : {df_trades.shape}")
    print(f"  Colonnes : {list(df_trades.columns)}")
    print(f"  Capital initial : {backtester.capital_initial:.2f} €")
    print(f"  Capital final : {df_trades['capital'].iloc[-1]:.2f} €")
    print(f"  PnL cumulé : {df_trades['pnl_cumule'].iloc[-1]:.2f} €")
    print(f"  Échantillon de trades :")
    print(df_trades[['position', 'pnl_quotidien', 'pnl_cumule', 'capital']].tail(10))
except Exception as e:
    print(f"Test 4 échoué : {e}")


# Test 5 : Calcul des métriques
print("\n--- Test 5 : Calcul des métriques de performance ---")

try:
    metriques = backtester.calculer_metriques(df_trades)
    print("Test 5 réussi !")
    print(f"  Rendement total : {metriques['rendement_total']:.2f} %")
    print(f"  Sharpe Ratio : {metriques['sharpe_ratio']:.2f}")
    print(f"  Maximum Drawdown : {metriques['max_drawdown']:.2f} %")
    print(f"  Win Rate : {metriques['win_rate']:.2f} %")
    print(f"  Nombre de trades : {metriques['nombre_trades']}")
except Exception as e:
    print(f"Test 5 échoué : {e}")