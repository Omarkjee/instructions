#!/usr/bin/env bash
# Deploys the Docker image to Azure Container Registry and creates an App Service using the image.
# Requires: az cli, docker, logged in (az login), and a Resource Group ready or will be created.

set -euo pipefail

RG=${1:-label-verifier-rg}
ACR_NAME=${2:-labelverifieracr$RANDOM}
APP_NAME=${3:-label-verifier-app-$RANDOM}
LOCATION=${4:-eastus}
IMAGE_TAG=label-verifier:latest

echo "Creating resource group $RG in $LOCATION"
az group create -n $RG -l $LOCATION

echo "Creating ACR $ACR_NAME"
az acr create -n $ACR_NAME -g $RG --sku Basic --admin-enabled true

echo "Logging in to ACR"
az acr login -n $ACR_NAME

echo "Building Docker image"
docker build -t $IMAGE_TAG .

echo "Tagging and pushing to ACR"
ACR_LOGIN_SERVER=$(az acr show -n $ACR_NAME -g $RG --query loginServer -o tsv)
docker tag $IMAGE_TAG $ACR_LOGIN_SERVER/$IMAGE_TAG
docker push $ACR_LOGIN_SERVER/$IMAGE_TAG

echo "Creating App Service plan"
az appservice plan create -g $RG -n ${APP_NAME}-plan --is-linux --sku B1

echo "Creating Web App from container"
az webapp create -g $RG -p ${APP_NAME}-plan -n $APP_NAME --deployment-container-image-name $ACR_LOGIN_SERVER/$IMAGE_TAG

echo "Configuring ACR access"
az webapp config container set -g $RG -n $APP_NAME --docker-custom-image-name $ACR_LOGIN_SERVER/$IMAGE_TAG --docker-registry-server-url https://$ACR_LOGIN_SERVER

echo "Done. App URL: https://$APP_NAME.azurewebsites.net"
