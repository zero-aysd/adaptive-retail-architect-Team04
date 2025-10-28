# Azure OpenAI Setup and Permissions Guide

## Overview
This guide provides detailed instructions to set up Azure OpenAI service, configure deployments, and assign necessary permissions for secure access.

## Step 1: Create Azure OpenAI Resource

1. Go to the Azure Portal.
2. Click on "Create a resource" and search for "Azure OpenAI".
3. Click "Create" and fill in the required details:
   - Subscription
   - Resource group
   - Region (choose supported region)
   - Name for the resource
4. Review and create the resource.

## Step 2: Generate API Keys and Endpoint

1. Navigate to your Azure OpenAI resource.
2. Select "Keys and Endpoint" from the left menu.
3. Copy the API key and endpoint URL for use in your application.

## Step 3: Create Model Deployment

1. In the Azure OpenAI resource, go to "Deployments".
2. Click "Create" to add a new deployment.
3. Choose the model you want to deploy (e.g., GPT-4, GPT-3.5).
4. Provide a deployment name (this will be used in your app configuration).
5. Create the deployment.

## Step 4: Assign Roles and Permissions

1. Identify the service principal or managed identity that your application will use.
2. Assign the **Cognitive Services User** role to this identity for the Azure OpenAI resource:
   ```bash
   az role assignment create \
     --assignee <service-principal-object-id> \
     --role "Cognitive Services User" \
     --scope $(az resource show --resource-group <resource-group> --name <openai-resource-name> --resource-type "Microsoft.CognitiveServices/accounts" --query id -o tsv)
   ```
3. Verify the role assignment:
   ```bash
   az role assignment list --assignee <service-principal-object-id> --scope <resource-id>
   ```

## Step 5: Configure Environment Variables

Set the following environment variables in your deployment environment or Azure Key Vault:

- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key.
- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint URL.
- `AZURE_OPENAI_DEPLOYMENT`: The deployment name of your model.

## Step 6: Test Azure OpenAI Access

Use Azure CLI or SDK to test connectivity:

```bash
az rest --method post --uri https://<your-endpoint>/openai/deployments/<deployment-name>/completions?api-version=2024-02-01-preview --body '{"prompt":"Hello, world!","max_tokens":5}'
```

## Additional Notes

- Ensure your Azure subscription supports Azure OpenAI service in the selected region.
- Keep your API keys secure and rotate them periodically.
- Use Azure Key Vault to manage secrets securely.
