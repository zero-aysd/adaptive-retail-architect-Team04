from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uuid
import time
import logging
from typing import Dict, Any
import os
from dotenv import load_dotenv
from datetime import datetime
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from app.graph import create_graph
from app.utils import load_env_file

load_env_file()

from .models import LayoutRequest, LayoutResponse, ErrorResponse
from .dependencies import get_keyvault_url


# Configure logging (integrate Langfuse later)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


KEYVAULT_URL = get_keyvault_url()
credential = DefaultAzureCredential()
secret_client = SecretClient(vault_url=KEYVAULT_URL, credential=credential)

# List of secrets to fetch
SECRETS = [
    "azure-openai-api-key",
    "azure-openai-endpoint",
    "azure-openai-api-version",
    "azure-openai-deployment",
    "azure-openai-embeddings",
    "langfuse-api-secret-key",
    "langfuse-public-key",
    "langfuse-host-endpoint",
    "pinecone-api-key"
]
app = FastAPI(
    title="Architect Co-pilot API",
    description="AI-powered adaptive retail layout generator",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Fetch secrets at startup
def load_secrets():
    for secret_name in SECRETS:
        try:
            secret = secret_client.get_secret(secret_name)
            # Convert secret name to env var format (e.g., azure-openai-api-key -> AZURE_OPENAI_API_KEY)
            env_name = secret_name.replace("-", "_").upper()
            os.environ[env_name] = secret.value
            print(f"✅ Loaded secret: {env_name}")
        except Exception as e:
            print(f"⚠ Failed to load secret {secret_name}: {str(e)}")

# Load secrets when the app starts
load_secrets()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "architect-copilot"}

@app.post("/generate_layout", response_model=LayoutResponse)
async def generate_layout(
    request: LayoutRequest,
    ):
    try:
        start_time = time.time()
        layout_id = str(uuid.uuid4())
        
        logger.info(f"Generating layout {layout_id} for {request.city}")
     
        
        render_time = time.time() - start_time
      
        logger.info(f"Layout {layout_id} generated in {render_time:.2f}s")
        return response
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            error_code="API_ERROR",
            timestamp=datetime.now()
        ).dict()
    )

if __name__ == "__main__":
    import uvicorn
    import os 
    for key, value in os.environ.items():
        print(f"{key}={value}")
    uvicorn.run(app, host="0.0.0.0", port=8000)