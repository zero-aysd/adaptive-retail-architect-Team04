# tools/rag_tool.py
from typing import List, Dict
from pydantic import BaseModel, Field
from langchain_openai import AzureOpenAIEmbeddings
from  pinecone import Pinecone
import os
from pathlib import Path

def load_env_file(env_path: str = ".env") -> None:
    """
    Manually load environment variables from a .env file
    without using external libraries like python-dotenv.

    Each line should follow the format:
        KEY=VALUE
    Lines starting with '#' are ignored.
    """
    env_file = Path(env_path)
    if not env_file.exists():
        print(f"⚠️  No .env file found at {env_path}. Using existing environment variables.")
        return

    with env_file.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key, value = key.strip(), value.strip().strip('"').strip("'")
            if key not in os.environ:  # don’t overwrite existing env vars
                os.environ[key] = value

load_env_file()
# --- Initialize Pinecone ---
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
if not PINECONE_API_KEY:
    raise ValueError("❌ Missing PINECONE_API_KEY environment variable.")

pc = Pinecone(api_key=PINECONE_API_KEY)

index_name = "retail-copilot"
if not pc.has_index(index_name):
    raise ValueError(f"❌ Pinecone index '{index_name}' not found.")

index = pc.Index(index_name)

# --- Initialize Azure Embeddings ---
embeddings = AzureOpenAIEmbeddings(
    azure_deployment="text-embedding-3-small",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    openai_api_version="2023-05-15"
)

# --- Input Schema ---
class RAGInput(BaseModel):
    query: str = Field(..., description="Natural language query to retrieve relevant documents.")
    top_k: int = Field(default=8, description="Number of top relevant chunks to retrieve.")

# --- RAG Tool Function ---
def rag_tool(input: RAGInput) -> Dict:
    """
    Retrieve relevant document chunks from Pinecone based on the input query.

    Args:
        input (RAGInput): Query and number of chunks to retrieve.

    Returns:
        dict: {
            "query": str,
            "retrieved_chunks": List[{"text": str, "source": str, "score": float}]
        }
    """
    try:
        # Embed the query
        q_emb = embeddings.embed_query(input.query)

        # Perform similarity search
        results = index.query(
            vector=q_emb,
            top_k=input.top_k,
            include_metadata=True
        )

        # Collect matched chunks
        chunks = []
        for match in results.matches:
            meta = match.metadata or {}
            chunks.append({
                "text": meta.get("text", ""),
                "source": meta.get("source", "unknown"),
                "score": match.score
            })

        return {
            "query": input.query,
            "retrieved_chunks": chunks
        }

    except Exception as e:
        return {"error": str(e)}


# --- DEMO SECTION ---
if __name__ == "__main__":
    """
    Simple demo to verify that the RAG tool is working end-to-end.
    Make sure environment variables are set:
        - AZURE_OPENAI_ENDPOINT
        - AZURE_OPENAI_API_KEY
        - PINECONE_API_KEY
    """
    print("🔍 Running demo for RAG tool...\n")

    sample_query = "What are the benefits of using cloud retail solutions?"
    rag_input = RAGInput(query=sample_query, top_k=5)

    output = rag_tool(rag_input)

    if "error" in output:
        print(f"❌ Error: {output['error']}")
    else:
        print(f"✅ Query: {output['query']}")
        print(f"Retrieved {len(output['retrieved_chunks'])} chunks:\n")
        for i, chunk in enumerate(output['retrieved_chunks'], 1):
            print(f"--- Chunk {i} ---")
            print(f"Source: {chunk['source']}")
            print(f"Score: {chunk['score']:.4f}")
            print(f"Text: {chunk['text'][:300]}...\n")
