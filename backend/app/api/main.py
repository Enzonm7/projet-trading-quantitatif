from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.routes import stocks
from backend.app.api.routes import pairs
from backend.app.api.routes import ml

# --- Création de l'application ---
app = FastAPI(
    title="Pairs Trading API",
    description="API REST pour la plateforme de trading quantitatif",
    version="1.0.0"
)

# --- Configuration CORS ---
origines_autorisees = [
    "http://localhost:3000",   # React (Create React App)
    "http://localhost:5173",   # React (Vite)
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origines_autorisees,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Routes de base ---
@app.get("/")
def lire_racine():
    """Route racine — vérifie que l'API est en ligne."""
    return {
        "message": "Pairs Trading API",
        "version": "1.0.0",
        "statut": "en ligne"
    }


@app.get("/health")
def verifier_sante():
    """Health check — utilisé pour monitoring et tests."""
    return {
        "statut": "ok",
        "timestamp": datetime.utcnow().isoformat()
    }

app.include_router(stocks.router, prefix="/api")
app.include_router(pairs.router, prefix="/api")
app.include_router(ml.router, prefix="/api")