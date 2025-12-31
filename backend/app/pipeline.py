"""
Module Pipeline pour l'orchestration du système de pairs trading.
"""

from backend.app.core.data_fetcher import DataFetcher
from backend.app.core.pairs_selector import PairsSelector
from backend.app.core.backtester import Backtester
from backend.app.core.risk_manager import RiskManager
from scipy import stats
from typing import Dict, Any


class TradingPipeline:
    """
    Orchestre le pipeline complet de pairs trading :
    DataFetcher → PairsSelector → Backtester → RiskManager
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialise le pipeline avec configuration.
        
        Args:
            config: Dictionnaire de configuration (optionnel)
                {
                    'capital_initial': 10000.0,
                    'seuil_entree': 2.0,
                    'seuil_sortie': 0.5,
                    'correlation_threshold': 0.7,
                    'pvalue_threshold': 0.05,
                    'max_position_size': 0.1,
                    'stop_loss_pct': 0.02,
                    'max_leverage': 1.0,
                    'cache_dir': './cache'
                }
        """
        # Configuration par défaut
        if config is None:
            config = {}
        
        # Initialisation des modules
        self.fetcher = DataFetcher(
            cache_dir=config.get('cache_dir', './cache')
        )
        
        self.selector = PairsSelector(
            correlation_threshold=config.get('correlation_threshold', 0.7),
            pvalue_threshold=config.get('pvalue_threshold', 0.05)
        )
        
        self.backtester = Backtester(
            capital_initial=config.get('capital_initial', 10000.0),
            seuil_entree=config.get('seuil_entree', 2.0),
            seuil_sortie=config.get('seuil_sortie', 0.5)
        )
        
        self.risk_manager = RiskManager(
            max_position_size=config.get('max_position_size', 0.1),
            stop_loss_pct=config.get('stop_loss_pct', 0.02),
            max_leverage=config.get('max_leverage', 1.0)
        )
        
        # Stocker la config
        self.config = config
    
    
    def executer_backtest(
        self, 
        ticker_a: str, 
        ticker_b: str, 
        start_date: str, 
        end_date: str,
        appliquer_risk_management: bool = True
    ) -> Dict[str, Any]:
        """
        Exécute un backtest complet sur une paire.
        
        Args:
            ticker_a: Premier ticker (ex: 'AAPL')
            ticker_b: Second ticker (ex: 'MSFT')
            start_date: Date de début 'YYYY-MM-DD'
            end_date: Date de fin 'YYYY-MM-DD'
            appliquer_risk_management: Appliquer la gestion du risque (défaut: True)
            
        Returns:
            Dictionnaire contenant:
                - pair_data: DataFrame des prix
                - is_cointegrated: Bool de cointégration
                - p_value: P-value du test ADF
                - ratio_couverture: Hedge ratio
                - spread: Série du spread
                - zscore: Série du z-score
                - df_signaux: DataFrame des signaux
                - df_trades: DataFrame des trades
                - df_risk: DataFrame avec risk management (si appliqué)
                - metriques: Métriques de performance
                - metriques_risque: Métriques de risque (si appliqué)
        """
        # 1. Téléchargement des données
        pair_data = self.fetcher.download_pair(ticker_a, ticker_b, start_date, end_date)
        prix_a = pair_data[f'Close_{ticker_a}']
        prix_b = pair_data[f'Close_{ticker_b}']
        
        # 2. Validation de la paire (cointégration)
        is_cointegrated, p_value = self.selector.test_cointegration(prix_a, prix_b)
        
        # 3. Calcul du ratio de couverture
        slope, intercept = stats.linregress(prix_b, prix_a)[:2]
        ratio_couverture = slope
        
        # 4. Backtesting
        spread = self.backtester.calculer_spread(prix_a, prix_b, ratio_couverture)
        zscore = self.backtester.calculer_zscore(spread, window=20)
        df_signaux = self.backtester.generer_signaux(zscore)
        df_trades = self.backtester.simuler_trades(df_signaux, prix_a, prix_b, ratio_couverture)
        metriques = self.backtester.calculer_metriques(df_trades)
        
        # 5. Gestion du risque (optionnel)
        df_risk = None
        metriques_risque = None
        
        if appliquer_risk_management:
            df_risk = self.risk_manager.appliquer_gestion_risque(
                df_trades,
                self.backtester.capital_initial,
                prix_a,
                prix_b
            )
            metriques_risque = self.risk_manager.calculer_metriques_risque(
                df_trades,
                self.backtester.capital_initial
            )
        
        # 6. Retourner tous les résultats
        return {
            'ticker_a': ticker_a,
            'ticker_b': ticker_b,
            'pair_data': pair_data,
            'is_cointegrated': is_cointegrated,
            'p_value': p_value,
            'ratio_couverture': ratio_couverture,
            'spread': spread,
            'zscore': zscore,
            'df_signaux': df_signaux,
            'df_trades': df_trades,
            'df_risk': df_risk,
            'metriques': metriques,
            'metriques_risque': metriques_risque
        }
    
    
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
        print(f"  Période : {resultats['pair_data'].index[0].date()} → {resultats['pair_data'].index[-1].date()}")
        print(f"  Nombre de jours : {len(resultats['pair_data'])}")
        
        # Validation statistique
        print(f"\n VALIDATION STATISTIQUE")
        print(f"  Cointégration : {'OUI' if resultats['is_cointegrated'] else 'NON'}")
        print(f"  P-value : {resultats['p_value']:.4f}")
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
            print(f"  Perte maximale : {metriques_risque['perte_max']:.2f} € ({metriques_risque['perte_max_pct']:.2f} %)")
            print(f"  Volatilité quotidienne : {metriques_risque['volatilite_quotidienne']:.4f} %")
            print(f"  VaR 95% : {metriques_risque['var_95']:.4f} %")
            print(f"  Ratio gain/perte : {metriques_risque['ratio_gain_perte']:.2f}")
            
            # Info stop-loss
            if resultats['df_risk'] is not None:
                stop_global = resultats['df_risk']['stop_loss_global'].any()
                stop_position = resultats['df_risk']['stop_loss_position'].any()
                print(f"\n  Stop-loss global déclenché : {'OUI' if stop_global else 'NON'}")
                print(f"  Stop-loss position déclenché : {'OUI' if stop_position else 'NON'}")
        
        # Capital final
        df_final = resultats['df_risk'] if resultats['df_risk'] is not None else resultats['df_trades']
        capital_initial = self.backtester.capital_initial
        capital_final = df_final['capital'].iloc[-1]
        
        print(f"\nCAPITAL")
        print(f"  Capital initial : {capital_initial:.2f} €")
        print(f"  Capital final : {capital_final:.2f} €")
        print(f"  Profit/Perte : {capital_final - capital_initial:.2f} €")
        
        print("\n" + "=" * 70)