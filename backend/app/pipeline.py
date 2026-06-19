"""
Module Pipeline pour l'orchestration du système de pairs trading.
"""

import pandas as pd 
from backend.app.core.data_fetcher import DataFetcher
from backend.app.core.data_source import DataSource
from backend.app.core.pairs_selector import PairsSelector
from backend.app.core.backtester import Backtester
from backend.app.core.risk_manager import RiskManager
from backend.app.core.strategies import MLEnhancedStrategy
from pathlib import Path
from typing import Dict, Any


class TradingPipeline:
    """
    Orchestre le pipeline complet de pairs trading :
    DataFetcher → PairsSelector → Backtester → RiskManager
    """
    
    def __init__(self, fetcher, selector, backtester, risk_manager):
        """
        Initialise le pipeline avec configuration.
        
        Args:
            fetcher (DataFetcher): Instance responsable de la récupération des données.
            selector (PairsSelector): Instance responsable de la sélection des paires.
            backtester (Backtester): Instance responsable de l'exécution de la stratégie.
            risk_manager (RiskManager): Instance responsable de la gestion du risque.
        """
        self.fetcher = fetcher
        self.selector = selector
        self.backtester = backtester
        self.risk_manager = risk_manager

    
    def executer_backtest(self, ticker_a: str, ticker_b: str, start_date: str, end_date: str, appliquer_risk_management: bool = True) -> Dict[str, Any]:
        """
        Exécute un backtest complet sur une paire.
        
        Args:
            ticker_a: Premier ticker (ex: 'AAPL')
            ticker_b: Second ticker (ex: 'MSFT')
            start_date: Date de début 'YYYY-MM-DD'
            end_date: Date de fin 'YYYY-MM-DD'
            appliquer_risk_management: Appliquer la gestion du risque (défaut: True)
            
        Returns:
            Dictionnaire avec les clés : ticker_a, ticker_b, donnees_paire,
            est_cointegree, p_valeur, ratio_couverture, spread, zscore,
            df_signaux, df_trades, df_risque, metriques, metriques_risque.
        """
        # 1. Téléchargement des données
        donnees_paire = self.fetcher.download_pair(ticker_a, ticker_b, start_date, end_date)
        prix_a = donnees_paire[f'Close_{ticker_a}']
        prix_b = donnees_paire[f'Close_{ticker_b}']
        
        # 2. Validation de la paire (cointégration)
        est_cointegree, p_valeur = self.selector.test_cointegration(prix_a, prix_b)
        
        # 3. Backtesting (DÉLÉGATION au Backtester)
        resultats_backtest = self.backtester.executer_backtest(prix_a, prix_b)
        
        # . Gestion du risque
        df_risque = None
        metriques_risque = None
        
        if appliquer_risk_management:
            df_risque = self.risk_manager.appliquer_gestion_risque(
                resultats_backtest['df_trades'],
                self.backtester.capital_initial,
                prix_a,
                prix_b
            )
            metriques_risque = self.risk_manager.calculer_metriques_risque(
                resultats_backtest['df_trades'],
                self.backtester.capital_initial
            )
        
        # 6. Retourner tous les résultats
        return {
            'ticker_a': ticker_a,
            'ticker_b': ticker_b,
            'donnees_paire': donnees_paire,
            'est_cointegree': est_cointegree,
            'p_valeur': p_valeur,
            'ratio_couverture': resultats_backtest['ratio'],
            'spread': resultats_backtest['df_signaux']['spread'],
            'zscore': resultats_backtest['df_signaux']['zscore'],
            'df_signaux': resultats_backtest['df_signaux'],
            'df_trades': resultats_backtest['df_trades'],
            'df_risque': df_risque,
            'metriques': resultats_backtest['metriques'],
            'metriques_risque': metriques_risque
        }
    
    def analyser_univers(self, tickers: list, start_date: str, end_date: str, appliquer_risk_management: bool = False) -> list:
        """
        Analyse toutes les paires possibles d'un univers de tickers.

        Args:
            tickers: Liste de symboles boursiers (ex: ['AAPL', 'MSFT', 'GOOGL'])
            start_date: Date de début 'YYYY-MM-DD'
            end_date: Date de fin 'YYYY-MM-DD'
            appliquer_risk_management: Appliquer le risk management (défaut: False)

        Returns:
            Liste de dictionnaires triée par Sharpe Ratio décroissant.
            Chaque dictionnaire contient :
                - paire: str (ex: 'AAPL-MSFT')
                - est_cointegree: bool
                - p_valeur: float
                - sharpe_ratio: float
                - rendement_total: float
                - max_drawdown: float
        """
        # 1. Générer toutes les combinaisons de paires
        combinaisons = self.selector.find_all_pairs(tickers)
        # 2. Pour chaque paire, executer_backtest()
        resultats_univers = []
        for ticker_a, ticker_b in combinaisons:
            try:
                print(f"Analyse {ticker_a}-{ticker_b}...")
                res = self.executer_backtest(ticker_a, ticker_b, start_date, end_date, appliquer_risk_management)
                # 3. Construire un dictionnaire résumé pour chaque paire réussie
                resume = {
                    'paire': f"{ticker_a}-{ticker_b}",
                    'est_cointegree': res['est_cointegree'],
                    'p_valeur': res['p_valeur'],
                    'sharpe_ratio': res['metriques']['sharpe_ratio'],  # dans metriques
                    'rendement_total': res['metriques']['rendement_total'],
                    'max_drawdown': res['metriques']['max_drawdown']
                }
                resultats_univers.append(resume)
            except Exception as e:
                print(f"Erreur {ticker_a}-{ticker_b}: {e}")

        # 4. Trier la liste par sharpe_ratio décroissant
        for i in range(len(resultats_univers)):
            for j in range(i + 1, len(resultats_univers)):
                if resultats_univers[j]['sharpe_ratio'] > resultats_univers[i]['sharpe_ratio']:
                    resultats_univers[i], resultats_univers[j] = resultats_univers[j], resultats_univers[i]

        return resultats_univers

    def sauvegarder_resultats(self, resultats: dict, dossier: str = "./data") -> None:
        """
        Sauvegarde les résultats d'un backtest en fichiers CSV.

        Args:
            resultats: Dictionnaire retourné par executer_backtest()
            dossier: Dossier de destination (défaut: ./data)

        Sauvegarde trois fichiers :
            - {ticker_a}_{ticker_b}_signaux.csv  ← resultats['df_signaux']
            - {ticker_a}_{ticker_b}_trades.csv   ← resultats['df_trades']
            - {ticker_a}_{ticker_b}_metriques.csv ← resultats['metriques'] converti en DataFrame
        """
        # 1. Créer le dossier s'il n'existe pas
        chemin_dossier = Path(dossier)
        chemin_dossier.mkdir(parents=True, exist_ok=True)

        # 2. Construire le préfixe à partir des tickers
        prefixe = f"{resultats['ticker_a']}_{resultats['ticker_b']}"

        # 3. Sauvegarder df_signaux
        resultats['df_signaux'].to_csv(chemin_dossier / f"{prefixe}_signaux.csv")

        # 4. Sauvegarder df_trades
        resultats['df_trades'].to_csv(chemin_dossier / f"{prefixe}_trades.csv")

        # 5. Convertir metriques en DataFrame et sauvegarder
        pd.DataFrame([resultats['metriques']]).to_csv(chemin_dossier / f"{prefixe}_metriques.csv")

        print(f"Résultats sauvegardés dans {dossier}/")
    
    
    def generer_rapport(self, resultats: Dict[str, Any]) -> None:
        """
        Affiche un rapport console des résultats.
        
        Args:
            resultats: Dictionnaire retourné par executer_backtest()
        """
        print("=" * 70)
        print("RAPPORT DE BACKTEST - PAIRS TRADING")
        print("=" * 70)
        
        # Informations générales
        print(f"\n PAIRE ANALYSÉE")
        print(f"  Ticker A : {resultats['ticker_a']}")
        print(f"  Ticker B : {resultats['ticker_b']}")
        print(f"  Période : {resultats['donnees_paire'].index[0].date()} → {resultats['donnees_paire'].index[-1].date()}")
        print(f"  Nombre de jours : {len(resultats['donnees_paire'])}")
        
        # Validation statistique
        print(f"\n VALIDATION STATISTIQUE")
        print(f"  Cointégration : {'OUI' if resultats['est_cointegree'] else 'NON'}")
        print(f"  P-value : {resultats['p_valeur']:.4f}")
        print(f"  Ratio de couverture : {resultats['ratio_couverture']:.4f}")
        
        # Métriques de performance
        metriques = resultats['metriques']
        print(f"\n PERFORMANCE")
        print(f"  Rendement total : {metriques['rendement_total']:.2f} %")
        print(f"  Sharpe Ratio : {metriques['sharpe_ratio']:.2f}")
        print(f"  Maximum Drawdown : {metriques['max_drawdown']:.2f} %")
        print(f"  Win Rate : {metriques['win_rate']:.2f} %")
        print(f"  Nombre de trades : {metriques['nombre_trades']}")
        
        # Métriques de risque (si disponibles)
        if resultats['metriques_risque'] is not None:
            metriques_risque = resultats['metriques_risque']
            print(f"\n  GESTION DU RISQUE")
            print(f"  Perte maximale : {metriques_risque['perte_maximale']:.2f} € ({metriques_risque['perte_maximale_pct']:.2f} %)")
            print(f"  Volatilité quotidienne : {metriques_risque['volatilite_quotidienne']:.4f} %")
            print(f"  VaR 95% : {metriques_risque['var_95']:.4f} %")
            print(f"  Ratio gain/perte : {metriques_risque['ratio_gain_perte']:.2f}")
            
            # Info stop-loss
            if resultats['df_risque'] is not None:
                stop_global = resultats['df_risque']['stop_loss_global'].any()
                stop_position = resultats['df_risque']['stop_loss_position'].any()
                print(f"\n  Stop-loss global déclenché : {'OUI' if stop_global else 'NON'}")
                print(f"  Stop-loss position déclenché : {'OUI' if stop_position else 'NON'}")
        
        # Capital final
        df_final = resultats['df_risque'] if resultats['df_risque'] is not None else resultats['df_trades']
        capital_initial = self.backtester.capital_initial
        capital_final = df_final['capital'].iloc[-1]
        
        print(f"\nCAPITAL")
        print(f"  Capital initial : {capital_initial:.2f} €")
        print(f"  Capital final : {capital_final:.2f} €")
        print(f"  Profit/Perte : {capital_final - capital_initial:.2f} €")
        
        print("\n" + "=" * 70)

    
    def comparer_strategies(self, ticker_a: str, ticker_b: str,
                            start_date: str, end_date: str,
                            strategie_ml: MLEnhancedStrategy) -> dict:
        """
        Compare les performances de la stratégie classique et ML-Enhanced.

        Args:
            ticker_a (str): Premier ticker.
            ticker_b (str): Second ticker.
            start_date (str): Date de début 'YYYY-MM-DD'.
            end_date (str): Date de fin 'YYYY-MM-DD'.
            strategie_ml (MLEnhancedStrategy): Stratégie ML instanciée et
                dont le classificateur est déjà entraîné.

        Returns:
            dict: Dictionnaire avec les clés :
                - 'classique' : dict de métriques (sharpe, rendement, drawdown, win_rate)
                - 'ml_enhanced' : dict de métriques (mêmes clés)
                - 'amelioration_sharpe' : float (différence de Sharpe ratio)
        """
        # 1. Télécharger les données une seule fois
        donnees = self.fetcher.download_pair(ticker_a, ticker_b, start_date, end_date)
        prix_a = donnees[f'Close_{ticker_a}']
        prix_b = donnees[f'Close_{ticker_b}']

        # 2. Backtest classique (self.backtester a déjà la strategie_base injectée)
        resultats_classique = self.backtester.executer_backtest(prix_a, prix_b)

        # 3. Backtest ML (Backtester temporaire avec strategie_ml)
        backtester_ml = Backtester(strategy=strategie_ml, capital_initial=self.backtester.capital_initial)
        resultats_ml = backtester_ml.executer_backtest(prix_a, prix_b)

        # 4. Construire et retourner le dictionnaire de comparaison
        return {
            'classique': resultats_classique['metriques'],
            'ml_enhanced': resultats_ml['metriques'],
            'amelioration_sharpe': round(resultats_ml['metriques']['sharpe_ratio'] - resultats_classique['metriques']['sharpe_ratio'], 2)
        }