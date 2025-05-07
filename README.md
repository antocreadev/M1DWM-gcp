# M1DWM-gcp


# Construire l'image
docker build -t fastapi-app .

# Lancer le conteneur
docker run -d -p 8080:8080 fastapi-app


docker build --platform linux/amd64 -t gcr.io/eminent-bond-459020-q4/fastapi-app .
docker push gcr.io/eminent-bond-459020-q4/fastapi-app
gcloud run deploy fastapi-api \
  --image gcr.io/eminent-bond-459020-q4/fastapi-app \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
