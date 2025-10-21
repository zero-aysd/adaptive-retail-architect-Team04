from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel
from typing import List
from ..rag.pipeline import query_rag
from ..models import LayoutRequest
from typing_extensions import Dict, List, Any

class LayoutPlan(BaseModel):
    zones: List[Dict[str, Any]]  # e.g., {"name": "Entrance", "area": 50, "fixtures": ["display_shelves"]}
    flow_path: List[str]  # e.g., ["entrance -> decompression -> main_display"]
    constraints_applied: List[str]

def generate_layout_plan(request: LayoutRequest, trends: Dict) -> Dict[str, Any]:
    """
    Layout Strategist: Synthesize RAG docs + trends into JSON plan.
    """
    query = f"Generate compliant layout for {request.city}: {request.design_focus}. Trends: {trends}. Constraints: {request.constraints}"
    docs = query_rag(query)
    
    # TODO: Use AzureChatOpenAI for real generation
    llm = AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        model="gpt-4"
    )
    
    prompt = ChatPromptTemplate.from_template(
        "As an expert retail architect, create a JSON layout plan using these docs: {docs}. Input: {query}"
    )
    chain = prompt | llm
    
    # Mock output for now
    plan = {
        "zones": [
            {"name": "Entrance Zone", "area": 80, "fixtures": ["welcome_display"], "position": "north"},
            {"name": "Main Display", "area": 250, "fixtures": ["shelving_units"], "position": "center", "products": trends.get("top_trends", [])},
            {"name": "Checkout", "area": 50, "fixtures": ["counter"], "position": "south"}
        ],
        "flow_path": ["entrance -> main -> checkout"],
        "constraints_applied": ["Avoided northern wall fixtures per lease"]
    }
    return plan