# rag/ingest.py
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
from pinecone import Pinecone, ServerlessSpec

# === Load environment variables ===
from app.utils import load_env_file
load_env_file()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "retail-copilot"

# === Initialize Pinecone client ===
pc = Pinecone(api_key=PINECONE_API_KEY)

# === Create index if not exists ===
existing_indexes = [index["name"] for index in pc.list_indexes()]
if INDEX_NAME not in existing_indexes:
    pc.create_index(
        name=INDEX_NAME,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",  # or "gcp"
            region="us-east-1"
        ),
    )
    print(f"✅ Created index: {INDEX_NAME}")
else:
    print(f"ℹ️ Using existing index: {INDEX_NAME}")

# === Connect to index ===
index = pc.Index(INDEX_NAME)

# === Embedding model ===
embeddings = AzureOpenAIEmbeddings(
    azure_deployment="text-embedding-3-small",
    openai_api_version="2023-05-15"
)

# === Text splitter ===
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

# === Ingest function ===
def ingest_document(file_path: str, source: str):
    """Load, split, embed, and upload document chunks to Pinecone index."""
    path = Path(file_path)
    if path.suffix == ".pdf":
        loader = PyPDFLoader(str(path))
    elif path.suffix == ".txt":
        loader = TextLoader(str(path))
    elif path.suffix == ".md":
        loader = UnstructuredMarkdownLoader(str(path))
    else:
        print(f"⚠️ Unsupported file type: {path.suffix}")
        return

    docs = loader.load()
    chunks = splitter.split_documents(docs)
    texts = [c.page_content for c in chunks]
    vectors = embeddings.embed_documents(texts)

    items = [
        {
            "id": f"{source}_{i}",
            "values": vec,
            "metadata": {"text": texts[i], "source": source, "chunk": i},
        }
        for i, vec in enumerate(vectors)
    ]

    index.upsert(vectors=items)
    print(f"✅ Ingested {len(items)} chunks from {source}")

# === Run once ===
if __name__ == "__main__":
    docs = [
        ("data/Blue_Retail_Brand_Book_v4.pdf", "brand_book"),
        ("data/Fixture_Catalog_Q3_2025.pdf", "fixture_catalog"),
        ("data/National_Building_Code_Accessibility_Chapter.txt", "building_code"),
        ("data/Store_Leasing_Agreement_Surat.pdf", "leasing_agreement"),
        ("data/Retail_Design_Best_Practices.md", "best_practices"),
    ]

    for fp, src in docs:
        ingest_document(fp, src)
