# M1DWM-gcp
# Construire l'image
docker build -t fastapi-app .

# Lancer le conteneur
docker run -d -p 8080:8080 fastapi-app

# Commande GCP

# Build l'image 
docker build --platform linux/amd64 -t gcr.io/eminent-bond-459020-q4/fastapi-app .

# Push l'image
docker push gcr.io/eminent-bond-459020-q4/fastapi-app

# Déployer
gcloud run deploy fastapi-api \
  --image gcr.io/eminent-bond-459020-q4/fastapi-app \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
