from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Ajouter le middleware CORS
app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],  # Autoriser toutes les origines
  allow_credentials=True,
  allow_methods=["*"],  # Autoriser toutes les méthodes HTTP
  allow_headers=["*"],  # Autoriser tous les en-têtes
)

@app.get("/")
def read_root():
  return {"message": "Bienvenue sur la page d'accueil !"}

@app.get("/bonjour")
def say_hello():
  return {"message": "Bonjour depuis FastAPI !"}
