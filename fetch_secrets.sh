#!/bin/bash
set -e

# -------------------------------
# CONFIGURATION
# -------------------------------
# Key Vault name (can be passed as env var or default)
KEYVAULT_NAME=${KEYVAULT_NAME:-"kv-capstone-team-four"}

# List of Key Vault secrets to fetch
SECRETS=("azure-openai-api-key" "azure-openai-endpoint" "azure-openai-api-version" \
         "azure-openai-deployment" "azure-openai-embeddings" \
         "langfuse-api-secret-key" "langfuse-public-key" "langfuse-host-endpoint" \
         "pinecone-api-key")

echo "Fetching secrets from Azure Key Vault: $KEYVAULT_NAME"

for secret in "${SECRETS[@]}"; do
    # Fetch secret value
    value=$(az keyvault secret show --vault-name $KEYVAULT_NAME --name $secret --query value -o tsv)
    
    if [ -z "$value" ]; then
        echo "⚠ Warning: Secret '$secret' not found or empty"
        continue
    fi

    # Export as environment variable (convert '-' to '_' for valid env var)
    env_name=$(echo "$secret" | tr '-' '_' | tr '[:lower:]' '[:upper:]')
    export "$env_name"="$value"
    echo "✅ Exported $env_name"
done

# -------------------------------
# START YOUR APP
# -------------------------------
# Replace this with your actual app start command
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
