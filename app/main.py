from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uuid
import time
import logging
import os
import base64
from app.graph import create_graph
from app.utils import load_env_file
from .models import LayoutRequest
from .dependencies import get_keyvault_url
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# === Setup ===
load_env_file()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Key Vault
KEYVAULT_URL = get_keyvault_url()
credential = DefaultAzureCredential()
secret_client = SecretClient(vault_url=KEYVAULT_URL, credential=credential)

SECRETS = [
    "azure-openai-api-key", "azure-openai-endpoint", "azure-openai-api-version",
    "azure-openai-deployment", "azure-openai-embeddings", "pinecone-api-key",
    "langfuses-secret-key",
    "langfuse-public-key",
    "langfuse-host-endpoint",
]

def load_secrets():
    for s in SECRETS:
        try:
            secret = secret_client.get_secret(s)
            os.environ[s.replace("-", "_").upper()] = secret.value
        except Exception as e:
            logger.warning(f"Secret {s} load failed: {e}")
load_secrets()

# === App ===
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# === Endpoint: Return Base64 Diagram Only ===
@app.post("/generate_layout")
async def generate_diagram(request: LayoutRequest):
    layout_id = str(uuid.uuid4())
    start = time.time()
    logger.info(f"Generating diagram (base64) | ID: {layout_id}")

    try:
        graph = create_graph()

        result = graph.invoke({
            "store_name": "Blue Retail Store",
            "city": request.city,
            "keywords": request.keywords or ["electronics"],
            "entrance_side": "south",
            "messages": [],
        })

        diagram_path = result.get("diagram_path")
        if not diagram_path or not os.path.exists(diagram_path):
            raise HTTPException(status_code=500, detail="Diagram file not generated")

        # Read and encode to base64
        with open(diagram_path, "rb") as img_file:
            base64_str = base64.b64encode(img_file.read()).decode("utf-8")

        logger.info(f"Diagram encoded to base64 in {time.time() - start:.2f}s")

        # Return ONLY base64

        return JSONResponse({
            "diagram_base64": base64_str
        })

    except Exception as e:
        logger.error(f"Diagram generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate diagram")
    

if __name__ == "__main__":
    import uvicorn
    # import os 
    # for key, value in os.environ.items():
    #     print(f"{key}={value}")
    uvicorn.run(app, host="0.0.0.0", port=8000)