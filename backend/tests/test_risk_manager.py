from backend.app.core.data_fetcher import DataFetcher
from backend.app.core.pairs_selector import PairsSelector
from backend.app.core.backtester import Backtester
from backend.app.core.risk_manager import RiskManager
from scipy import stats

# Initialisation des modules
fetcher = DataFetcher()
selector = PairsSelector(correlation_threshold=0.7, pvalue_threshold=0.05)
backtester = Backtester(capital_initial=10000.0, seuil_entree=2.0, seuil_sortie=0.5)
risk_manager = RiskManager(max_position_size=0.1, stop_loss_pct=0.02, max_leverage=1.0)

# Téléchargement des données pour une paire (AAPL-MSFT)
print("\n--- Téléchargement des données ---")
pair_data = fetcher.download_pair("AAPL", "MSFT", "2023-01-01", "2024-01-01")
print(f"Données téléchargées : {pair_data.shape}")
print(f"Colonnes : {list(pair_data.columns)}")

# Extraction des prix de clôture
prix_aapl = pair_data['Close_AAPL']
prix_msft = pair_data['Close_MSFT']

# Calcul du ratio de couverture (hedge ratio)
print("\n--- Calcul du ratio de couverture ---")
slope, intercept = stats.linregress(prix_msft, prix_aapl)[:2]
ratio_couverture = slope
print(f"Ratio de couverture (hedge ratio) : {ratio_couverture:.4f}")

# Backtesting complet (nécessaire pour les tests RiskManager)
print("\n--- Backtesting ---")
spread = backtester.calculer_spread(prix_aapl, prix_msft, ratio_couverture)
zscore = backtester.calculer_zscore(spread, window=20)
df_signaux = backtester.generer_signaux(zscore)
df_trades = backtester.simuler_trades(df_signaux, prix_aapl, prix_msft, ratio_couverture)
print(f"Backtesting terminé : {df_trades.shape}")


# Test 1 : Calcul de la taille de position
print("\n--- Test 1 : Calcul de la taille de position ---")

try:
    capital = 10000.0
    
    # Sans volatilité
    taille_sans_vol = risk_manager.calculer_taille_position(capital)
    print("Test 1a réussi !")
    print(f"  Capital : {capital:.2f} €")
    print(f"  Taille position (sans volatilité) : {taille_sans_vol:.2f} €")
    print(f"  Pourcentage : {(taille_sans_vol/capital)*100:.2f} %")
    
    # Avec volatilité faible
    taille_vol_faible = risk_manager.calculer_taille_position(capital, volatilite=0.01)
    print("\nTest 1b réussi !")
    print(f"  Taille position (volatilité faible 0.01) : {taille_vol_faible:.2f} €")
    
    # Avec volatilité élevée
    taille_vol_elevee = risk_manager.calculer_taille_position(capital, volatilite=0.05)
    print("\nTest 1c réussi !")
    print(f"  Taille position (volatilité élevée 0.05) : {taille_vol_elevee:.2f} €")
    print(f"  Impact volatilité : {((taille_vol_faible - taille_vol_elevee)/taille_vol_faible)*100:.2f} % de réduction")
    
except Exception as e:
    print(f"Test 1 échoué : {e}")


# Test 2 : Vérification stop-loss global
print("\n--- Test 2 : Vérification stop-loss global ---")

try:
    capital_initial = 10000.0
    
    # Cas 1 : Pas de stop-loss
    capital_ok = 9850.0
    stop_ok, perte_ok = risk_manager.verifier_stop_loss(capital_initial, capital_ok)
    print("Test 2a réussi !")
    print(f"  Capital initial : {capital_initial:.2f} €")
    print(f"  Capital actuel : {capital_ok:.2f} €")
    print(f"  Perte : {perte_ok*100:.2f} %")
    print(f"  Stop-loss déclenché : {stop_ok}")
    
    # Cas 2 : Stop-loss déclenché
    capital_stop = 9750.0
    stop_declenche, perte_stop = risk_manager.verifier_stop_loss(capital_initial, capital_stop)
    print("\nTest 2b réussi !")
    print(f"  Capital actuel : {capital_stop:.2f} €")
    print(f"  Perte : {perte_stop*100:.2f} %")
    print(f"  Stop-loss déclenché : {stop_declenche}")
    
except Exception as e:
    print(f"Test 2 échoué : {e}")


# Test 3 : Vérification stop-loss position
print("\n--- Test 3 : Vérification stop-loss position ---")

try:
    # Position LONG
    prix_entree_long = 150.0
    prix_actuel_ok = 148.0
    prix_actuel_stop = 142.0
    
    stop_long_ok = risk_manager.verifier_stop_loss_position(prix_entree_long, prix_actuel_ok, 1)
    stop_long_declenche = risk_manager.verifier_stop_loss_position(prix_entree_long, prix_actuel_stop, 1)
    
    print("Test 3a réussi (LONG) !")
    print(f"  Prix entrée : {prix_entree_long:.2f} €")
    print(f"  Prix actuel OK : {prix_actuel_ok:.2f} € → Stop : {stop_long_ok}")
    print(f"  Prix actuel STOP : {prix_actuel_stop:.2f} € → Stop : {stop_long_declenche}")
    
    # Position SHORT
    prix_entree_short = 150.0
    prix_actuel_ok_short = 152.0
    prix_actuel_stop_short = 158.0
    
    stop_short_ok = risk_manager.verifier_stop_loss_position(prix_entree_short, prix_actuel_ok_short, -1)
    stop_short_declenche = risk_manager.verifier_stop_loss_position(prix_entree_short, prix_actuel_stop_short, -1)
    
    print("\nTest 3b réussi (SHORT) !")
    print(f"  Prix entrée : {prix_entree_short:.2f} €")
    print(f"  Prix actuel OK : {prix_actuel_ok_short:.2f} € → Stop : {stop_short_ok}")
    print(f"  Prix actuel STOP : {prix_actuel_stop_short:.2f} € → Stop : {stop_short_declenche}")
    
except Exception as e:
    print(f"Test 3 échoué : {e}")


# Test 4 : Ajustement du leverage
print("\n--- Test 4 : Ajustement du leverage ---")

try:
    capital = 10000.0
    
    # Sharpe faible (pas de leverage)
    leverage_faible = risk_manager.ajuster_leverage(0.5, capital)
    print("Test 4a réussi !")
    print(f"  Sharpe Ratio : 0.5")
    print(f"  Leverage ajusté : {leverage_faible:.2f}x")
    
    # Sharpe moyen
    leverage_moyen = risk_manager.ajuster_leverage(1.5, capital)
    print("\nTest 4b réussi !")
    print(f"  Sharpe Ratio : 1.5")
    print(f"  Leverage ajusté : {leverage_moyen:.2f}x")
    
    # Sharpe élevé
    leverage_eleve = risk_manager.ajuster_leverage(3.0, capital)
    print("\nTest 4c réussi !")
    print(f"  Sharpe Ratio : 3.0")
    print(f"  Leverage ajusté : {leverage_eleve:.2f}x")
    print(f"  Leverage max autorisé : {risk_manager.max_leverage:.2f}x")
    
except Exception as e:
    print(f"Test 4 échoué : {e}")


# Test 5 : Application de la gestion du risque
print("\n--- Test 5 : Application de la gestion du risque ---")

try:
    df_trades_avec_risque = risk_manager.appliquer_gestion_risque(
        df_trades, 
        backtester.capital_initial,
        prix_aapl,
        prix_msft
    )
    print("Test 5 réussi !")
    print(f"  Shape : {df_trades_avec_risque.shape}")
    print(f"  Nouvelles colonnes : {[col for col in df_trades_avec_risque.columns if col not in df_trades.columns]}")
    print(f"  Stop-loss global déclenché : {df_trades_avec_risque['stop_loss_global'].any()}")
    print(f"  Stop-loss position déclenché : {df_trades_avec_risque['stop_loss_position'].any()}")
    print(f"  Échantillon :")
    print(df_trades_avec_risque[['position', 'capital', 'stop_loss_global', 'stop_loss_position', 'taille_position']].tail(10))
    
except Exception as e:
    print(f"Test 5 échoué : {e}")


# Test 6 : Calcul des métriques de risque
print("\n--- Test 6 : Calcul des métriques de risque ---")

try:
    metriques_risque = risk_manager.calculer_metriques_risque(df_trades, backtester.capital_initial)
    print("Test 6 réussi !")
    print(f"  Perte maximale : {metriques_risque['perte_max']:.2f} €")
    print(f"  Perte maximale : {metriques_risque['perte_max_pct']:.2f} %")
    print(f"  Volatilité quotidienne : {metriques_risque['volatilite_quotidienne']:.4f} %")
    print(f"  VaR 95% : {metriques_risque['var_95']:.4f} %")
    print(f"  Ratio gain/perte : {metriques_risque['ratio_gain_perte']:.2f}")
    
except Exception as e:
    print(f"Test 6 échoué : {e}")