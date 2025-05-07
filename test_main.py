from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_read_root():
    """Test que la route racine retourne le bon message."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Bienvenue sur la page d'accueil !"}
