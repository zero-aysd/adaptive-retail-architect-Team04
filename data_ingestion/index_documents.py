import os
from typing import List, Optional
from pathlib import Path

from langchain_community.document_loaders import (
    DirectoryLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
    PyMuPDFLoader  # or PyPDFLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

def create_loaders(source_folder: str) -> DirectoryLoader:
    """
    Create DirectoryLoader with appropriate loaders for different file types.
    
    Args:
        source_folder: Path to the source folder containing documents
        
    Returns:
        DirectoryLoader configured with multiple file type loaders
    """
    # Define loader for each file type
    loader_cls_map = {
        ".txt": TextLoader,
        ".md": UnstructuredMarkdownLoader,
        ".markdown": UnstructuredMarkdownLoader,
        ".pdf": PyMuPDFLoader,  # More efficient than PyPDFLoader for embeddings
    }
    
    def custom_loader(path: str) -> List:
        """Custom loader function that selects appropriate loader based on file extension"""
        ext = Path(path).suffix.lower()
        if ext in loader_cls_map:
            return loader_cls_map[ext](path).load()
        else:
            print(f"Skipping unsupported file: {path}")
            return []
    
    return DirectoryLoader(
        source_folder,
        glob="**/*",
        loader_cls=custom_loader,
        show_progress=True,
        silent_errors=True
    )

def index_documents(
    source_folder: str,
    pinecone_api_key: str,
    pinecone_index_name: str,
    azure_openai_deployment: str,
    azure_openai_api_key: str,
    azure_openai_endpoint: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    index_if_exists: str = "update",  # "create", "update", "skip"
    namespace: Optional[str] = None
) -> PineconeVectorStore:
    """
    Load documents from source folder, split them, embed with Azure OpenAI,
    and index to Pinecone.
    
    Args:
        source_folder: Path to folder containing .txt, .md, .pdf files
        pinecone_api_key: Pinecone API key
        pinecone_index_name: Name of Pinecone index
        azure_openai_deployment: Azure OpenAI deployment name for text-embedding-3-small
        azure_openai_api_key: Azure OpenAI API key
        azure_openai_endpoint: Azure OpenAI endpoint URL
        chunk_size: Size of text chunks for splitting
        chunk_overlap: Overlap between chunks
        index_if_exists: "create" (delete and recreate), "update" (add/update), "skip" (skip if exists)
        namespace: Optional Pinecone namespace
        
    Returns:
        PineconeVectorStore instance
    """
    
    # Initialize Pinecone client
    pc = Pinecone(api_key=pinecone_api_key)
    
    # Check if index exists and handle accordingly
    available_indexes = pc.list_indexes().names()
    
    if pinecone_index_name in available_indexes:
        if index_if_exists == "skip":
            print(f"Index '{pinecone_index_name}' already exists. Skipping.")
            index = pc.Index(pinecone_index_name)
            return PineconeVectorStore.from_existing_index(
                pinecone_index_name,
                AzureOpenAIEmbeddings(
                    azure_deployment=azure_openai_deployment,
                    azure_endpoint=azure_openai_endpoint,
                    api_key=azure_openai_api_key,
                    model="text-embedding-3-small",
                    dimensions=1536  # text-embedding-3-small dimension
                ),
                namespace=namespace
            )
        elif index_if_exists == "create":
            print(f"Deleting existing index '{pinecone_index_name}'...")
            pc.delete_index(pinecone_index_name)
    
    # Create index if it doesn't exist
    if pinecone_index_name not in available_indexes or index_if_exists == "create":
        print(f"Creating Pinecone index '{pinecone_index_name}'...")
        pc.create_index(
            name=pinecone_index_name,
            dimension=1536,  # text-embedding-3-small dimension
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
        # Wait for index to be ready
        while not pc.describe_index(pinecone_index_name).status["ready"]:
            print("Waiting for index to be ready...")
            time.sleep(10)
    
    # Initialize Azure OpenAI embeddings
    embeddings = AzureOpenAIEmbeddings(
        azure_deployment=azure_openai_deployment,
        azure_endpoint=azure_openai_endpoint,
        api_key=azure_openai_api_key,
        model="text-embedding-3-small",
        dimensions=1536
    )
    
    # Load documents
    print(f"Loading documents from {source_folder}...")
    loader = create_loaders(source_folder)
    docs = loader.load()
    print(f"Loaded {len(docs)} documents")
    
    if not docs:
        raise ValueError("No documents found in source folder")
    
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    print("Splitting documents into chunks...")
    splits = text_splitter.split_documents(docs)
    print(f"Created {len(splits)} text chunks")
    
    # Create vector store and add documents
    print("Creating/updating Pinecone vector store...")
    vectorstore = PineconeVectorStore.from_documents(
        documents=splits,
        embedding=embeddings,
        index_name=pinecone_index_name,
        namespace=namespace
    )
    
    print(f"Successfully indexed {len(splits)} chunks to Pinecone index '{pinecone_index_name}'")
    return vectorstore

# Example usage
if __name__ == "__main__":
    import time
    
    # Configuration
    SOURCE_FOLDER = "./documents"  # Folder containing your .txt, .md, .pdf files
    PINECONE_API_KEY = "your-pinecone-api-key"
    PINECONE_INDEX_NAME = "my-document-index"
    AZURE_OPENAI_DEPLOYMENT = "text-embedding-3-small-deployment"  # Your deployment name
    AZURE_OPENAI_API_KEY = "your-azure-openai-api-key"
    AZURE_OPENAI_ENDPOINT = "https://your-resource-name.openai.azure.com/"
    
    try:
        # Index documents
        vectorstore = index_documents(
            source_folder=SOURCE_FOLDER,
            pinecone_api_key=PINECONE_API_KEY,
            pinecone_index_name=PINECONE_INDEX_NAME,
            azure_openai_deployment=AZURE_OPENAI_DEPLOYMENT,
            azure_openai_api_key=AZURE_OPENAI_API_KEY,
            azure_openai_endpoint=AZURE_OPENAI_ENDPOINT,
            chunk_size=1000,
            chunk_overlap=200,
            index_if_exists="update",  # or "create" to recreate index
            namespace="documents-v1"
        )
        
        print("Indexing completed successfully!")
        
        # Optional: Test similarity search
        query = "What is this document about?"
        results = vectorstore.similarity_search(query, k=3)
        print("\nSample similarity search results:")
        for i, doc in enumerate(results, 1):
            print(f"{i}. {doc.page_content[:200]}...")
            
    except Exception as e:
        print(f"Error during indexing: {str(e)}")