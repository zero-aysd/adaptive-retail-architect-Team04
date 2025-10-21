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
# load_dotenv()

from .models import LayoutRequest, LayoutResponse, ErrorResponse
from .dependencies import get_api_key, get_azure_openai_client, get_pinecone_index
from .agents.market_analyst import get_local_trends
from .agents.layout_strategist import generate_layout_plan
from .agents.draftsman import generate_diagram

# Configure logging (integrate Langfuse later)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


KEYVAULT_URL = "https://kv-capstone-team-four.vault.azure.net/"
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
    api_key: str = Depends(get_api_key)
):
    try:
        start_time = time.time()
        layout_id = str(uuid.uuid4())
        
        logger.info(f"Generating layout {layout_id} for {request.city}")
        
        # Step 1: Market Analyst
        trends = get_local_trends(request.city, request.target_products or ["electronics"])
        
        # Step 2: Layout Strategist (RAG + LLM)
        plan = generate_layout_plan(request, trends)
        
        # Step 3: AI Draftsman
        diagram_b64 = generate_diagram(plan)
        
        render_time = time.time() - start_time
        
        response = LayoutResponse(
            success=True,
            layout_id=layout_id,
            layout_data=plan,
            diagram_url=diagram_b64,
            trends_summary=trends,
            render_time=render_time,
            generated_at=datetime.now(),
            metadata={
                "city": request.city,
                "store_area": request.store_area,
                "constraints": request.constraints
            }
        )
        
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