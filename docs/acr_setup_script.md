# Push Docker Image to Azure Container Registry (ACR)

This guide explains how to push your Docker image to Azure Container Registry (ACR).

---

## Setup Variables
```bash
ACR_NAME=genai4capstoneaayushsoni
RESOURCE_GROUP=Tredence-B4
IMAGE_NAME=architect-copilot-aayush-soni
TAG=latest
```

## Makee sure you have ACR push Permissions
```bash
az role assignment list --assignee $(az ad signed-in-user show --query id -o tsv) --scope $(az acr show --name genai4capstoneaayushsoni --query id -o tsv) --output table

```
If not, assign the role:
```bash
az role assignment create \
  --assignee $(az ad signed-in-user show --query id -o tsv) \
  --role AcrPush \
  --scope $(az acr show --name $ACR_NAME --query id -o tsv)


```
## 🧩 1. Log in to Azure

```bash
az login
```

If you have multiple subscriptions:
```bash
az account set --subscription "<your-subscription-id-or-name>"
```

---

## 🧩 2. Log in to ACR

```bash
az acr login --name $ACR_NAME
```

✅ Authenticates Docker with your ACR instance.

---

## 🧩 3. Verify ACR Login Server

```bash
az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query "loginServer" --output tsv
```
Expected output:
```
genai4capstoneaayushsoni.azurecr.io
```

---

## 🧩 4. Build the docker Image

Make sure you are in the same directory as your Dockerfile.

```bash
docker build -t $ACR_NAME.azurecr.io/$IMAGE_NAME:$TAG .
```

---

## 🧩 5. Push Image to ACR

```bash
docker push $ACR_NAME.azurecr.io/$IMAGE_NAME:$TAG
```

---

## 🧩 6. Verify the Image in ACR

List repositories:

```bash
az acr repository list --name $ACR_NAME --output table
az acr repository show-tags --name $ACR_NAME --repository $IMAGE_NAME --output table
```


# Key Vault Setup And Adding Secrets

```bash
KEYVAULT_NAME=kv-capstone-team-four
LOCATION=centralindia
az keyvault create --name $KEYVAULT_NAME --resource-group $RESOURCE_GROUP --location $LOCATION

# Example secrets
az keyvault secret set --vault-name $KEYVAULT_NAME --name "OPENAI-API-KEY" --value "<your-key>"



```
## For Local testing create and verify the ROLE

Verify Key Vault Permissions:
Check if your Azure account has the necessary permissions (e.g., "Key Vault Secrets User") to read secrets:
```bash
az role assignment list \
  --assignee $(az ad signed-in-user show --query id -o tsv) \
  --scope $(az keyvault show --name $KEYVAULT_NAME --resource-group $RESOURCE_GROUP --query id -o tsv) \
  --output table
  ```
If no role is listed, assign it:
```bash
az role assignment create \
  --assignee $(az ad signed-in-user show --query id -o tsv) \
  --role "Key Vault Secrets User" \
  --scope $(az keyvault show --name $KEYVAULT_NAME --resource-group Tredence-B4 --query id -o tsv)


## Cleanup Keyvault

```bash

az keyvault delete --name $KEYVAULT_NAME --resource-group $RESOURCE_GROUP
az keyvault purge --name $KEYVAULT_NAME
```
### Create a service Principal for Keyvault Access to Azure Container Instance
Create a service principal:
```bash
az ad sp create-for-rbac \
  --name "capstone-sp" \
  --role "Key Vault Secrets User" \
  --scopes $(az keyvault show --name $KEYVAULT_NAME  --resource-group $RESOURCE_GROUP --query id -o tsv)
  
```
Note the appId, password, and tenant.
Step 1: Verify Service Principal Existence and Retrieve Credentials
The az ad sp create-for-rbac command outputs the appId, password, and tenant when run, but if you no longer have this output, you can retrieve most details (except the password, which requires a reset if lost).


Find the Service Principal:
Use the display name capstone-sp to locate the service principal:
```bash 
az ad sp list \
  --display-name capstone-sp \
  --query "[].{appId:appId, displayName:displayName, objectId:id, tenantId:tenantId}" \
  --output table 
  ```
Expected Output:
textAppId                                 DisplayName    ObjectId                              TenantId
------------------------------------  -------------  ------------------------------------  ------------------------------------
<appId>                               capstone-sp    <objectId>                            <tenantId>

appId: The application ID (e.g., 67060e7e-d382-4ef9-8a09-2e4583d7dc16).
objectId: The service principal’s object ID in Azure AD.
tenantId: The Azure AD tenant ID (e.g., 0d2a6053-e113-42e7-9169-f5cbed7a941f).
If no results appear, the service principal wasn’t created or was deleted. Recreate it (Step 4).



Retrieve Password (If Lost):
The password is only shown during creation and isn’t stored in a retrievable format. If you don’t have it, reset the credentials:
```bash
az ad sp credential reset \
  --id <appId> \
  --query "{appId:appId, password:password, tenant:tenant}" \
  --output table
  ```
Expected Output:
textAppId                                 Password                              Tenant
------------------------------------  ------------------------------------  ------------------------------------
<appId>                               <new-password>                        <tenantId>

Save the password securely (e.g., in a local file with restricted permissions or a password manager).
Note: This resets the existing password, invalidating any previous one.

# Deploy Docker Image From Azure Container Registry to Azure Container Instance

## ⚙️ Step 1: Login and Set Environment Variables

```bash
# Login to Azure
az login

# (Optional) Select correct subscription
az account set --subscription "<YOUR_SUBSCRIPTION_NAME_OR_ID>"

# Set variables
ACR_NAME=genai4capstoneaayushsoni
RESOURCE_GROUP=Tredence-B4
ACI_NAME=architect-copilot-aci
CONTAINER_NAME=architect-copilot-container
IMAGE_NAME=architect-copilot-aayush-soni:latest
DNS_LABEL=architect-copilot-aayushsoni2025   
LOCATION=centralindia
AZURE_CLIENT_ID=<appId> 
AZURE_CLIENT_SECRET=<password> 
AZURE_TENANT_ID=<tenant>

az group show --name $RESOURCE_GROUP --output table
```


## Step 2: Check your ACR Permissions 
```bash
az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --output table
```
If that works, verify if you have AcrPull or AcrPush roles:
```bash
az role assignment list \
  --assignee $(az ad signed-in-user show --query id -o tsv) \
  --scope $(az acr show --name $ACR_NAME --query id -o tsv) \
  --output table
```
If you don't see AcrPull or AcrPush run 
```bash
az role assignment create \
  --assignee $(az ad signed-in-user show --query id -o tsv) \
  --role AcrPull \
  --scope $(az acr show --name $ACR_NAME --query id -o tsv)
```

## Step 3: Enable and Retrieve ACR Credentials
```bash
az acr update -n $ACR_NAME --admin-enabled true
az acr credential show -n $ACR_NAME
```
Copy the username and password fields — you’ll use them in the next step.



## Step 4: Deploy the Image to ACI


```bash
az container create \
  --resource-group $RESOURCE_GROUP \
  --name $ACI_NAME \
  --image $ACR_NAME.azurecr.io/$IMAGE_NAME \
  --registry-login-server $ACR_NAME.azurecr.io \
  --registry-username <username_from_previous_command> \
  --registry-password <password_from_previous_command> \
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

## Step 5: Verify Deployment
Check container status:

```bash
az container show \
  --resource-group $RESOURCE_GROUP \
  --name $ACI_NAME \
  --query "{Status:instanceView.state, IP:ipAddress.ip, FQDN:ipAddress.fqdn}" \
  --output table
```

## Step 6: Access Your Application:
Visit your app in the browser:
```bash
http://<FQDN_from_above_output>
```

Example:
```bash
http://architect-copilot-aayushsoni2025.eastus.azurecontainer.io
```




## Step 7: Cleanup(Optional)
When you are done testing:
```bash
az container delete --name $ACI_NAME --resource-group $RESOURCE_GROUP --yes
```





