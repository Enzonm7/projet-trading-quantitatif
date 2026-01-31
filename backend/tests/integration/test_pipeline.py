from backend.app.pipeline import TradingPipeline

# Test 1 : Pipeline avec configuration par défaut
print("\n--- Test 1 : Pipeline avec configuration par défaut ---")

try:
    pipeline = TradingPipeline()
    print("Test 1 réussi !")
    print(f"  Capital initial : {pipeline.backtester.capital_initial:.2f} €")
    print(f"  Seuil entrée : {pipeline.backtester.seuil_entree}")
    print(f"  Seuil sortie : {pipeline.backtester.seuil_sortie}")
    print(f"  Correlation threshold : {pipeline.selector.correlation_threshold}")
    print(f"  P-value threshold : {pipeline.selector.pvalue_threshold}")
except Exception as e:
    print(f"Test 1 échoué : {e}")


# Test 2 : Pipeline avec configuration personnalisée
print("\n--- Test 2 : Pipeline avec configuration personnalisée ---")

try:
    config = {
        'capital_initial': 15000.0,
        'seuil_entree': 2.5,
        'seuil_sortie': 0.3,
        'correlation_threshold': 0.8,
        'pvalue_threshold': 0.01,
        'max_position_size': 0.15,
        'stop_loss_pct': 0.03,
        'max_leverage': 2.0
    }
    
    pipeline_custom = TradingPipeline(config)
    print("Test 2 réussi !")
    print(f"  Capital initial : {pipeline_custom.backtester.capital_initial:.2f} €")
    print(f"  Seuil entrée : {pipeline_custom.backtester.seuil_entree}")
    print(f"  Max position size : {pipeline_custom.risk_manager.max_position_size}")
    print(f"  Stop-loss : {pipeline_custom.risk_manager.stop_loss_pct*100:.0f} %")
except Exception as e:
    print(f"Test 2 échoué : {e}")


# Test 3 : Exécution backtest complet AVEC risk management
print("\n--- Test 3 : Backtest complet AVEC risk management ---")

try:
    resultats = pipeline.executer_backtest(
        ticker_a='AAPL',
        ticker_b='MSFT',
        start_date='2023-01-01',
        end_date='2024-01-01',
        appliquer_risk_management=True
    )
    
    print("Test 3 réussi !")
    print(f"  Paire : {resultats['ticker_a']}-{resultats['ticker_b']}")
    print(f"  Données : {resultats['pair_data'].shape}")
    print(f"  Cointégration : {resultats['is_cointegrated']}")
    print(f"  P-value : {resultats['p_value']:.4f}")
    print(f"  Ratio couverture : {resultats['ratio_couverture']:.4f}")
    print(f"  Trades : {resultats['df_trades'].shape}")
    print(f"  Risk management appliqué : {resultats['df_risk'] is not None}")
    print(f"  Métriques risque disponibles : {resultats['metriques_risque'] is not None}")
    
except Exception as e:
    print(f"Test 3 échoué : {e}")


# Test 4 : Exécution backtest SANS risk management
print("\n--- Test 4 : Backtest complet SANS risk management ---")

try:
    resultats_no_risk = pipeline.executer_backtest(
        ticker_a='GOOGL',
        ticker_b='META',
        start_date='2023-01-01',
        end_date='2024-01-01',
        appliquer_risk_management=False
    )
    
    print("Test 4 réussi !")
    print(f"  Paire : {resultats_no_risk['ticker_a']}-{resultats_no_risk['ticker_b']}")
    print(f"  Risk management appliqué : {resultats_no_risk['df_risk'] is not None}")
    print(f"  Métriques risque disponibles : {resultats_no_risk['metriques_risque'] is not None}")
    print(f"  Métriques performance disponibles : {resultats_no_risk['metriques'] is not None}")
    
except Exception as e:
    print(f"Test 4 échoué : {e}")


# Test 5 : Génération du rapport (paire AAPL-MSFT)
print("\n--- Test 5 : Génération du rapport ---")

try:
    pipeline.generer_rapport(resultats)
    print("\nTest 5 réussi !")
    
except Exception as e:
    print(f"Test 5 échoué : {e}")


# Test 6 : Vérification du contenu du dictionnaire resultats
print("\n--- Test 6 : Vérification des clés du dictionnaire resultats ---")

try:
    cles_attendues = [
        'ticker_a', 'ticker_b', 'pair_data', 'is_cointegrated', 
        'p_value', 'ratio_couverture', 'spread', 'zscore',
        'df_signaux', 'df_trades', 'df_risk', 'metriques', 'metriques_risque'
    ]
    
    cles_presentes = list(resultats.keys())
    
    print("Test 6 réussi !")
    print(f"  Clés attendues : {len(cles_attendues)}")
    print(f"  Clés présentes : {len(cles_presentes)}")
    print(f"  Toutes les clés présentes : {all(cle in cles_presentes for cle in cles_attendues)}")
    
    print(f"\n  Clés disponibles :")
    for cle in cles_presentes:
        type_valeur = type(resultats[cle]).__name__
        print(f"    - {cle}: {type_valeur}")
    
except Exception as e:
    print(f"Test 6 échoué : {e}")


# Test 7 : Comparaison de plusieurs paires
print("\n--- Test 7 : Comparaison de plusieurs paires ---")

try:
    paires = [
        ('AAPL', 'MSFT'),
        ('JPM', 'BAC'),
        ('PEP', 'KO')
    ]
    
    print("Test 7 - Analyse de 3 paires")
    comparaison = []
    
    for ticker_a, ticker_b in paires:
        res = pipeline.executer_backtest(
            ticker_a, ticker_b,
            '2023-01-01', '2024-01-01',
            appliquer_risk_management=True
        )
        
        comparaison.append({
            'paire': f"{ticker_a}-{ticker_b}",
            'cointegree': res['is_cointegrated'],
            'p_value': res['p_value'],
            'rendement': res['metriques']['rendement_total'],
            'sharpe': res['metriques']['sharpe_ratio'],
            'drawdown': res['metriques']['max_drawdown']
        })
    
    print("Test 7 réussi !\n")
    print("  Résumé comparatif :")
    print(f"  {'Paire':<15} {'Coint.':<8} {'P-value':<10} {'Rend.%':<10} {'Sharpe':<8} {'DD%':<10}")
    print("  " + "-" * 70)
    
    for comp in comparaison:
        print(f"  {comp['paire']:<15} {str(comp['cointegree']):<8} {comp['p_value']:<10.4f} {comp['rendement']:<10.2f} {comp['sharpe']:<8.2f} {comp['drawdown']:<10.2f}")
    
except Exception as e:
    print(f"Test 7 échoué : {e}")
