import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import MetaData, Table, Column, Integer, String
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.future import select
from dotenv import load_dotenv

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


@app.on_event("startup")
async def startup():
    # Crée la table si elle n'existe pas déjà
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)


@app.get("/")
async def read_root():
    return {"message": "Bienvenue sur la page d'accueil !"}


@app.get("/test-db")
async def test_db():
    async with engine.connect() as conn:
        result = await conn.execute("SELECT NOW()")
        row = result.fetchone()
        return {"db_time": str(row[0])}


@app.get("/add-user/{name}/{age}")
async def add_user(name: str, age: int):
    # Utilisation de begin() pour créer une transaction et commit automatiquement à la fin
    async with engine.begin() as conn:
        # Insertion d'un nouvel utilisateur dans la base de données
        await conn.execute(users.insert().values(name=name, age=age))
        # Le commit est automatique avec engine.begin()
    return {"message": f"User {name} added with age {age}"}


@app.get("/get-users")
async def get_users():
    async with engine.connect() as conn:
        # Sélection de tous les utilisateurs de la table
        result = await conn.execute(select(users))
        users_list = result.fetchall()
        return {
            "users": [
                {"id": user[0], "name": user[1], "age": user[2]} for user in users_list
            ]
        }
