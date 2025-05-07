import os
from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import MetaData, Table, Column, Integer, String
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.future import select
from dotenv import load_dotenv
# Import du monitoring Prometheus
from prometheus_client import Counter, Histogram
from starlette_prometheus import PrometheusMiddleware, metrics

# Charger les variables d'environnement à partir du fichier .env si disponible
load_dotenv(verbose=True, dotenv_path=".env", override=True)

# Récupérer l'URL de la base de données depuis les variables d'environnement
DATABASE_URL = os.getenv("DATABASE_URL")

# Vérifier que DATABASE_URL est défini
if not DATABASE_URL:
    raise ValueError("La variable d'environnement DATABASE_URL n'est pas définie")

# Création du moteur de connexion à la base de données avec asyncpg comme driver
engine = create_async_engine(DATABASE_URL, echo=True)

# Définition de la table "users"
metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("age", Integer, nullable=False),
)

# Création de l'application FastAPI
app = FastAPI()

# Ajouter le middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Autoriser toutes les origines
    allow_credentials=True,
    allow_methods=["*"],  # Autoriser toutes les méthodes HTTP
    allow_headers=["*"],  # Autoriser tous les en-têtes
)

# Ajouter le middleware Prometheus pour le monitoring
app.add_middleware(PrometheusMiddleware)
# Exposer les métriques Prometheus
app.add_route("/metrics", metrics)

# Créer quelques métriques personnalisées
REQUEST_COUNT = Counter(
    "app_request_count", 
    "Nombre total de requêtes", 
    ["method", "endpoint", "http_status"]
)
REQUEST_LATENCY = Histogram(
    "app_request_latency_seconds", 
    "Latence des requêtes en secondes",
    ["method", "endpoint"]
)


@app.on_event("startup")
async def startup():
    # Crée la table si elle n'existe pas déjà
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)


@app.get("/")
async def read_root():
    REQUEST_COUNT.labels(method="GET", endpoint="/", http_status=200).inc()
    with REQUEST_LATENCY.labels(method="GET", endpoint="/").time():
        return {"message": "Bienvenue sur la page d'accueil !"}


@app.get("/health")
async def health_check(response: Response):
    """Endpoint de vérification de l'état de santé pour le monitoring."""
    try:
        # Vérification de la connexion à la base de données
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        
        # Tout est OK
        REQUEST_COUNT.labels(method="GET", endpoint="/health", http_status=200).inc()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        # Problème avec la base de données
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        REQUEST_COUNT.labels(method="GET", endpoint="/health", http_status=503).inc()
        return {"status": "unhealthy", "database": str(e)}


@app.get("/test-db")
async def test_db():
    REQUEST_COUNT.labels(method="GET", endpoint="/test-db", http_status=200).inc()
    with REQUEST_LATENCY.labels(method="GET", endpoint="/test-db").time():
        async with engine.connect() as conn:
            result = await conn.execute("SELECT NOW()")
            row = result.fetchone()
            return {"db_time": str(row[0])}


@app.get("/add-user/{name}/{age}")
async def add_user(name: str, age: int):
    REQUEST_COUNT.labels(method="GET", endpoint="/add-user", http_status=200).inc()
    with REQUEST_LATENCY.labels(method="GET", endpoint="/add-user").time():
        # Utilisation de begin() pour créer une transaction et commit automatiquement à la fin
        async with engine.begin() as conn:
            # Insertion d'un nouvel utilisateur dans la base de données
            await conn.execute(users.insert().values(name=name, age=age))
            # Le commit est automatique avec engine.begin()
        return {"message": f"User {name} added with age {age}"}


@app.get("/get-users")
async def get_users():
    REQUEST_COUNT.labels(method="GET", endpoint="/get-users", http_status=200).inc()
    with REQUEST_LATENCY.labels(method="GET", endpoint="/get-users").time():
        async with engine.connect() as conn:
            # Sélection de tous les utilisateurs de la table
            result = await conn.execute(select(users))
            users_list = result.fetchall()
            return {
                "users": [
                    {"id": user[0], "name": user[1], "age": user[2]} for user in users_list
                ]
            }
