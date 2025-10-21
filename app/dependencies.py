from fastapi import HTTPException, Depends, status, Header
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

async def get_api_key(api_key: Optional[str] = Header(None)) -> str:
    """Dependency to validate API key"""
    allowed_keys = os.getenv("ALLOWED_API_KEYS", "").split(",")
    if api_key and api_key in allowed_keys:
        return api_key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API key"
    )

async def get_azure_openai_client():
    """Placeholder for Azure OpenAI client"""
    # TODO: Implement with azure-openai package
    return {"model": "gpt-4", "api_key": os.getenv("AZURE_OPENAI_KEY")}

async def get_pinecone_index():
    """Placeholder for Pinecone index"""
    # TODO: Implement with pinecone-client
    return {"index_name": os.getenv("PINECONE_INDEX_NAME")}