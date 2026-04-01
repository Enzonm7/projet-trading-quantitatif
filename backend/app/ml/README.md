# Module ML — Pairs Trading

Ce module implémente le pipeline de Machine Learning de la plateforme de backtesting.
Il transforme des données de prix brutes en prédictions sur la convergence du spread
d'une paire d'actifs, en utilisant XGBoost comme modèle de classification.

---

## Structure des fichiers

| Fichier | Classe | Rôle |
|--------|--------|------|
| `feature_engineer.py` | `FeatureEngineer` | Calcule les indicateurs techniques (RSI, Bollinger, volatilité, corrélation glissante) à partir des prix bruts  |
| `dataset_builder.py` | `DatasetBuilder` | Labellise les données et effectue le split temporel 70/15/15 |
| `xgboost_classifier.py` | `XGBoostClassifier` | Entraîne, optimise et évalue le modèle XGBoost |

---

## Pipeline ML

```
FeatureEngineer → DatasetBuilder → XGBoostClassifier
```

**Étape 1 — Création des features (`FeatureEngineer`)**  
Les prix bruts ne sont pas directement exploitables par un modèle ML.
`FeatureEngineer` les transforme en indicateurs techniques :
RSI, Bandes de Bollinger, volatilité annualisée glissante, et corrélation glissante.
Ces indicateurs capturent le comportement dynamique de la paire sur différentes fenêtres temporelles.

**Étape 2 — Préparation du dataset (`DatasetBuilder`)**  
`DatasetBuilder` crée les labels (convergence/divergence) par labellisation forward-looking
sur un horizon de 5 jours, puis découpe les données en trois splits chronologiques
stricts (70% train / 15% validation / 15% test) sans mélange aléatoire.

**Étape 3 — Entraînement et évaluation (`XGBoostClassifier`)**  
`XGBoostClassifier` standardise les features, entraîne le modèle, optimise ses
hyperparamètres par GridSearch + TimeSeriesSplit, puis évalue ses performances
sur le jeu de test.

---

## Concepts clés

**Pourquoi XGBoost ?**  
XGBoost est un algorithme de gradient boosting : il construit une succession d'arbres
de décision, chacun corrigeant les erreurs du précédent. Il est robuste au bruit,
rapide à entraîner, et particulièrement adapté aux données financières.
Il a été préféré à LSTM pour sa simplicité d'entraînement et son interprétabilité
(feature importance).

**Pourquoi log-returns ?**  
Les prix bruts varient fortement d'un actif à l'autre et ne sont pas stationnaires.
Les log-returns (log(prix_t / prix_t-1)) transforment ces prix en variations relatives,
rendant les séries comparables entre actifs et stables dans le temps — une propriété
indispensable pour la qualité du z-score et des features ML.

**Pourquoi un split temporel strict ?**  
Mélanger aléatoirement des données financières temporelles crée du data leakage :
le modèle voit des données futures pendant l'entraînement, ce qui fausse
artificiellement ses performances. Le split par `iloc` sans mélange garantit
que le modèle n'est jamais entraîné sur des données postérieures à celles qu'il prédit.

**Labellisation forward-looking**  
Pour chaque jour t, on regarde le z-score 5 jours plus tard :
- Si |zscore[t+5]| < |zscore[t]| → le spread converge → label **1**
- Sinon → le spread diverge → label **0**

C'est la vérité terrain que le modèle cherche à reproduire.

---

## Exemple d'utilisation
```python

from backend.app.ml.feature_engineer import FeatureEngineer
from backend.app.ml.dataset_builder import DatasetBuilder
from backend.app.ml.xgboost_classifier import XGBoostClassifier

# Préparation des données
fe = FeatureEngineer()
builder = DatasetBuilder(feature_engineer=fe)
df_train, df_val, df_test = builder.preparer_dataset(df)

X_train = df_train.drop(columns=["target"])
y_train = df_train["target"].values
X_test = df_test.drop(columns=["target"])
y_test = df_test["target"].values

# Route 1 : Entraînement rapide
clf = XGBoostClassifier()
clf.train(X_train, y_train)
predictions = clf.predict(X_test)

# Route 2 : Entraînement optimisé
clf = XGBoostClassifier()
clf.optimiser_hyperparametres(X_train, y_train)
metriques = clf.evaluer(X_test, y_test)
print(metriques)
```

---

## Métriques d'évaluation

| Métrique | Description |
|----------|-------------|
| Accuracy | Taux de prédictions correctes sur l'ensemble des observations |
| Precision | Parmi les convergences prédites, proportion de vraies convergences |
| Recall | Parmi les vraies convergences, proportion correctement détectées |
| F1 | Moyenne harmonique de Precision et Recall — métrique principale car robuste au déséquilibre des classes |
| ROC-AUC | Capacité du modèle à distinguer les deux classes sur tous les seuils (0.5 = aléatoire, 1.0 = parfait) |

---

## Lancer les tests
```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Tests du module ML
pytest backend/tests/unit/test_feature_engineer.py -v
pytest backend/tests/unit/test_xgboost_classifier.py -v
pytest backend/tests/unit/test_dataset_builder.py -v
```