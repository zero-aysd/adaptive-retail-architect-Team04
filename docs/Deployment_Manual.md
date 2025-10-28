# Deployment Manual for AI Co-pilot on Azure

## Prerequisites
- Azure CLI installed and logged in (`az login`)
- Appropriate Azure subscription and permissions
- Docker installed locally for building images

## Step 1: Setup Azure Container Registry (ACR)

1. Define variables:
```bash
ACR_NAME=genai4capstoneaayushsoni
RESOURCE_GROUP=Tredence-B4
IMAGE_NAME=architect-copilot-aayush-soni
TAG=latest
```

2. Ensure you have ACR push permissions:
```bash
az role assignment list --assignee $(az ad signed-in-user show --query id -o tsv) --scope $(az acr show --name $ACR_NAME --query id -o tsv) --output table
```

3. If not, assign the AcrPush role:
```bash
az role assignment create \
  --assignee $(az ad signed-in-user show --query id -o tsv) \
  --role AcrPush \
  --scope $(az acr show --name $ACR_NAME --query id -o tsv)
```

4. Login to ACR:
```bash
az acr login --name $ACR_NAME
```

5. Verify ACR login server:
```bash
az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query "loginServer" --output tsv
```

## Step 2: Build and Push Docker Image

1. Build the Docker image:
```bash
docker build -t $ACR_NAME.azurecr.io/$IMAGE_NAME:$TAG .
```

2. Push the image to ACR:
```bash
docker push $ACR_NAME.azurecr.io/$IMAGE_NAME:$TAG
```

3. Verify the image in ACR:
```bash
az acr repository list --name $ACR_NAME --output table
az acr repository show-tags --name $ACR_NAME --repository $IMAGE_NAME --output table
```

## Step 3: Setup Azure Key Vault and Secrets

1. Create Key Vault:
```bash
KEYVAULT_NAME=kv-capstone-team-four
LOCATION=centralindia
az keyvault create --name $KEYVAULT_NAME --resource-group $RESOURCE_GROUP --location $LOCATION
```

2. Add secrets (example):
```bash
az keyvault secret set --vault-name $KEYVAULT_NAME --name "AZURE-OPENAI-API-KEY" --value "<your-api-key>"
az keyvault secret set --vault-name $KEYVAULT_NAME --name "AZURE-OPENAI-ENDPOINT" --value "<your-endpoint>"
az keyvault secret set --vault-name $KEYVAULT_NAME --name "AZURE-OPENAI-DEPLOYMENT" --value "<your-deployment-name>"
```

3. Verify Key Vault permissions:
```bash
az role assignment list \
  --assignee $(az ad signed-in-user show --query id -o tsv) \
  --scope $(az keyvault show --name $KEYVAULT_NAME --resource-group $RESOURCE_GROUP --query id -o tsv) \
  --output table
```

4. Assign "Key Vault Secrets User" role if missing:
```bash
az role assignment create \
  --assignee $(az ad signed-in-user show --query id -o tsv) \
  --role "Key Vault Secrets User" \
  --scope $(az keyvault show --name $KEYVAULT_NAME --resource-group $RESOURCE_GROUP --query id -o tsv)
```

## Step 4: Create Service Principal for Key Vault Access

1. Create service principal:
```bash
az ad sp create-for-rbac \
  --name "capstone-sp" \
  --role "Key Vault Secrets User" \
  --scopes $(az keyvault show --name $KEYVAULT_NAME --resource-group $RESOURCE_GROUP --query id -o tsv)
```

2. Note the `appId`, `password`, and `tenant` from the output.

3. If password is lost, reset credentials:
```bash
az ad sp credential reset \
  --id <appId> \
  --query "{appId:appId, password:password, tenant:tenant}" \
  --output table
```

## Step 5: Deploy to Azure Container Instance (ACI)

1. Set environment variables:
```bash
ACI_NAME=architect-copilot-aci
CONTAINER_NAME=architect-copilot-container
DNS_LABEL=architect-copilot-aayushsoni2025
LOCATION=centralindia
AZURE_CLIENT_ID=<appId>
AZURE_CLIENT_SECRET=<password>
AZURE_TENANT_ID=<tenant>
```

2. Create container instance:
```bash
az container create \
  --resource-group $RESOURCE_GROUP \
  --name $ACI_NAME \
  --image $ACR_NAME.azurecr.io/$IMAGE_NAME:$TAG \
  --registry-login-server $ACR_NAME.azurecr.io \
  --registry-username <username_from_acr_credentials> \
  --registry-password <password_from_acr_credentials> \
  --assign-identity \
  --cpu 1 \
  --memory 2 \
  --os-type Linux \
  --ports 8000 \
  --dns-name-label $DNS_LABEL \
  --restart-policy Always \
  --environment-variables \
    AZURE_CLIENT_ID=$AZURE_CLIENT_ID \
    AZURE_CLIENT_SECRET=$AZURE_CLIENT_SECRET \
    AZURE_TENANT_ID=$AZURE_TENANT_ID
```

3. Verify deployment:
```bash
az container show \
  --resource-group $RESOURCE_GROUP \
  --name $ACI_NAME \
  --query "{Status:instanceView.state, IP:ipAddress.ip, FQDN:ipAddress.fqdn}" \
  --output table
```

4. Access the application via the FQDN URL.

## Step 6: Cleanup (Optional)

Delete container instance when done:
```bash
az container delete --name $ACI_NAME --resource-group $RESOURCE_GROUP --yes
```

## Additional Notes

- Ensure Azure OpenAI resource is properly configured with deployment and keys.
- Assign necessary roles to service principals for secure access.
- Use Azure Key Vault to securely manage secrets and API keys.
