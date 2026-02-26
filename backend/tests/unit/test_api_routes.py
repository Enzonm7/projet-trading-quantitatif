"""
Tests unitaires pour les routes API.
Pattern AAA (Arrange-Act-Assert).
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from backend.app.api.main import app
from backend.app.database.base import get_db


# ========== HELPERS ==========

def creer_prix_mock(tickers: list, n_jours: int = 100) -> dict:
    """Génère des séries de prix synthétiques fortement corrélées."""
    np.random.seed(42)
    dates = pd.date_range("2021-01-01", periods=n_jours, freq="B")
    base = np.cumsum(np.random.randn(n_jours))
    return {
        ticker: pd.DataFrame(
            {"Close": 100 + base + np.random.randn(n_jours) * 0.1},
            index=dates
        )
        for ticker in tickers
    }


# ========== FAKE DB ==========

class FakeDB:
    """Fausse session DB pour éviter toute connexion PostgreSQL dans les tests."""
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def close(self): pass


# ========== TESTS ==========

class TestRoutesBase:
    """Tests pour GET / et GET /health."""

    @pytest.fixture
    def client(self):
        """Fixture : client de test avec DB mockée."""
        def override_get_db():
            yield FakeDB()

        app.dependency_overrides[get_db] = override_get_db
        yield TestClient(app)
        app.dependency_overrides.clear()

    def test_racine_retourne_200(self, client):
        """GET / doit retourner 200."""
        # ACT
        response = client.get("/")
        # ASSERT
        assert response.status_code == 200

    def test_racine_contient_message(self, client):
        """GET / doit contenir le champ message."""
        # ACT
        response = client.get("/")
        # ASSERT
        assert "message" in response.json()

    def test_health_retourne_200(self, client):
        """GET /health doit retourner 200."""
        # ACT
        response = client.get("/health")
        # ASSERT
        assert response.status_code == 200

    def test_health_statut_ok(self, client):
        """GET /health doit retourner statut == ok."""
        # ACT
        response = client.get("/health")
        # ASSERT
        assert response.json()["statut"] == "ok"

    def test_health_contient_timestamp(self, client):
        """GET /health doit contenir le champ timestamp."""
        # ACT
        response = client.get("/health")
        # ASSERT
        assert "timestamp" in response.json()


class TestRouteStocks:
    """Tests pour GET /api/stocks/{ticker}."""

    @pytest.fixture
    def client(self, monkeypatch):
        """Fixture : client de test avec DB et DataFetcher mockés."""
        def override_get_db():
            yield FakeDB()

        app.dependency_overrides[get_db] = override_get_db

        dates = pd.date_range("2021-01-01", periods=5, freq="B")
        df_mock = pd.DataFrame(
            {"Close": [150.0, 151.0, 152.0, 153.0, 154.0]},
            index=dates
        )

        fake_fetcher = MagicMock()
        fake_fetcher.get_cached_data.return_value = df_mock
        monkeypatch.setattr("app.api.routes.stocks.DataFetcher", lambda *a, **kw: fake_fetcher)

        yield TestClient(app)
        app.dependency_overrides.clear()

    def test_ticker_valide_retourne_200(self, client):
        """GET /api/stocks/AAPL avec données mockées doit retourner 200."""
        # ACT
        response = client.get("/api/stocks/AAPL?date_debut=2021-01-01&date_fin=2024-01-01")
        # ASSERT
        assert response.status_code == 200

    def test_ticker_invalide_retourne_404(self, monkeypatch):
        """GET /api/stocks/TICKER_INVALIDE doit retourner 404."""
        # ARRANGE
        def override_get_db():
            yield FakeDB()

        app.dependency_overrides[get_db] = override_get_db

        fake_fetcher = MagicMock()
        fake_fetcher.get_cached_data.side_effect = ValueError("ticker inconnu")
        monkeypatch.setattr("app.api.routes.stocks.DataFetcher", lambda *a, **kw: fake_fetcher)

        client = TestClient(app)
        # ACT
        response = client.get("/api/stocks/TICKER_INVALIDE")
        # ASSERT
        assert response.status_code == 404
        app.dependency_overrides.clear()


class TestRouteDetectPairs:
    """Tests pour POST /api/pairs/detect."""

    @pytest.fixture
    def client(self, monkeypatch):
        """Fixture : client de test avec DB et DataFetcher mockés."""
        def override_get_db():
            yield FakeDB()

        app.dependency_overrides[get_db] = override_get_db

        tickers = ["AAPL", "MSFT", "GOOGL"]
        prix_mock = creer_prix_mock(tickers)

        fake_fetcher = MagicMock()
        fake_fetcher.get_cached_data.side_effect = lambda ticker, *args: prix_mock[ticker]
        monkeypatch.setattr("app.api.routes.pairs.DataFetcher", lambda *a, **kw: fake_fetcher)

        yield TestClient(app)
        app.dependency_overrides.clear()

    def test_requete_valide_retourne_200(self, client):
        """POST /api/pairs/detect avec 3 tickers valides doit retourner 200."""
        # ACT
        response = client.post("/api/pairs/detect", json={
            "tickers": ["AAPL", "MSFT", "GOOGL"],
            "date_debut": "2021-01-01",
            "date_fin": "2024-01-01"
        })
        # ASSERT
        assert response.status_code == 200

    def test_reponse_contient_champs_attendus(self, client):
        """La réponse doit contenir nombre_paires et paires."""
        # ACT
        response = client.post("/api/pairs/detect", json={
            "tickers": ["AAPL", "MSFT"],
            "date_debut": "2021-01-01",
            "date_fin": "2024-01-01"
        })
        # ASSERT
        data = response.json()
        assert "nombre_paires" in data
        assert "paires" in data

    def test_paires_detectees_avec_seuils_permissifs(self, client):
        """Avec des seuils permissifs et données corrélées, au moins 1 paire doit être détectée."""
        # ACT
        response = client.post("/api/pairs/detect", json={
            "tickers": ["AAPL", "MSFT"],
            "date_debut": "2021-01-01",
            "date_fin": "2024-01-01",
            "seuil_correlation": 0.5,
            "seuil_pvalue": 0.1
        })
        # ASSERT
        assert response.json()["nombre_paires"] >= 1

    def test_nombre_paires_coherent(self, client):
        """nombre_paires doit être égal à len(paires)."""
        # ACT
        response = client.post("/api/pairs/detect", json={
            "tickers": ["AAPL", "MSFT", "GOOGL"],
            "date_debut": "2021-01-01",
            "date_fin": "2024-01-01",
            "seuil_correlation": 0.5,
            "seuil_pvalue": 0.1
        })
        # ASSERT
        data = response.json()
        assert data["nombre_paires"] == len(data["paires"])

    def test_un_seul_ticker_retourne_422(self, client):
        """Une liste avec un seul ticker doit être rejetée avec 422."""
        # ACT
        response = client.post("/api/pairs/detect", json={
            "tickers": ["AAPL"],
            "date_debut": "2021-01-01",
            "date_fin": "2024-01-01"
        })
        # ASSERT
        assert response.status_code == 422

    def test_ticker_invalide_retourne_404(self, monkeypatch):
        """Un ticker invalide doit retourner 404."""
        # ARRANGE
        def override_get_db():
            yield FakeDB()

        app.dependency_overrides[get_db] = override_get_db

        fake_fetcher = MagicMock()
        fake_fetcher.get_cached_data.side_effect = ValueError("ticker inconnu")
        monkeypatch.setattr("app.api.routes.pairs.DataFetcher", lambda *a, **kw: fake_fetcher)

        client = TestClient(app)
        # ACT
        response = client.post("/api/pairs/detect", json={
            "tickers": ["AAPL", "TICKER_INVALIDE"],
            "date_debut": "2021-01-01",
            "date_fin": "2024-01-01"
        })
        # ASSERT
        assert response.status_code == 404
        app.dependency_overrides.clear()