#!/bin/bash

# Load environment variables from .env file
export $(grep -v '^#' .env | xargs)
KEYVAULT_NAME=kv-capstone-team-four

# Set secrets in Azure Key Vault with valid names
az keyvault secret set --vault-name $KEYVAULT_NAME --name "azure-openai-api-key" --value "$AZURE_OPENAI_API_KEY"
az keyvault secret set --vault-name $KEYVAULT_NAME --name "azure-openai-endpoint" --value "$AZURE_OPENAI_ENDPOINT"
az keyvault secret set --vault-name $KEYVAULT_NAME --name "azure-openai-api-version" --value "$AZURE_OPENAI_API_VERSION"
az keyvault secret set --vault-name $KEYVAULT_NAME --name "azure-openai-deployment" --value "$AZURE_OPENAI_DEPLOYMENT"
az keyvault secret set --vault-name $KEYVAULT_NAME --name "azure-openai-embeddings" --value "$AZURE_OPENA_EMBEDDINGS"
az keyvault secret set --vault-name $KEYVAULT_NAME --name "langfuse-api-secret-key" --value "$LANGFUSE_API_SECRET_KEY"
az keyvault secret set --vault-name $KEYVAULT_NAME --name "langfuse-public-key" --value "$LANGFUSE_PUBLIC_KEY"
az keyvault secret set --vault-name $KEYVAULT_NAME --name "langfuse-host-endpoint" --value "$LANGFUSE_HOST_ENDPOINT"
az keyvault secret set --vault-name $KEYVAULT_NAME --name "pinecone-api-key" --value "$PINECONE_API_KEY"
