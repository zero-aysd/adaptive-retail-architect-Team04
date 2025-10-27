from fastapi import HTTPException, Depends, status, Header
from typing import Optional
import os
from app.utils import load_env_file

load_env_file()



async def get_api_key(api_key: Optional[str] = Header(None)) -> str:
    """Dependency to validate API key"""
    allowed_keys = os.getenv("ALLOWED_API_KEYS", "").split(",")
    if api_key and api_key in allowed_keys:
        return api_key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API key"
    )
def get_keyvault_url() -> str:
    """Dependency to validate API key"""
    return "https://kv-capstone-team-four.vault.azure.net/"
    