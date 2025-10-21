from langchain_pinecone import Pinecone
from langchain_openai import AzureOpenAIEmbeddings
from pinecone import Pinecone as PineconeClient
from typing_extensions import List, Dict, Any
import os

def query_rag(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    RAG retrieval from Pinecone index (documents: brand book, fixtures, codes, lease).
    """
    # TODO: Initialize real Pinecone and Azure embeddings
    pc = PineconeClient(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))
    embeddings = AzureOpenAIEmbeddings(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        model="text-embedding-ada-002"
    )
    
    # Mock retrieval for now
    mock_chunks = [
        {"content": "No permanent fixtures on northern wall (from Surat lease).", "source": "Store_Leasing_Agreement_Surat.pdf"},
        {"content": "Aisle width min 1.2m for accessibility (NBC 2016).", "source": "National_Building_Code_Accessibility_Chapter.txt"},
        {"content": "Use blue color palette for branding.", "source": "Blue_Retail_Brand_Book_v4.pdf"}
    ]
    return mock_chunks[:top_k]