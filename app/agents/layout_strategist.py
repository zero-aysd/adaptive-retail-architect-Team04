# agents/strategist_subgraph.py
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
import operator
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.output_parsers import PydanticOutputParser
from app.tools.rag_tool import rag_tool, RAGInput
from app.schemas.layout import LayoutPlan
import json
from app.utils import load_env_file
from app.prompt_loader import PromptManager
import os
# from langfuse.decorators import observe

# === Load Environment ===
load_env_file()

# === LLM Setup ===
llm = AzureChatOpenAI(
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
    temperature=0
)

# Test connection
try:
    llm.invoke("hello")
    print("LLM connected successfully.")
except Exception as e:
    print(f"LLM connection failed: {e}")

# === Prompts ===
PLANNER_PROMPT = PromptManager.get("layout_strategist")
REVIEWER_PROMPT = PromptManager.get("reviewer")

# === Parser ===
parser = PydanticOutputParser(pydantic_object=LayoutPlan)

# === Tools ===
tools = [rag_tool]

# === Enriched ToolNode to populate `retrieved` ===
class RetrievalEnrichedToolNode(ToolNode):
    def __call__(self, state: 'StrategistState'):
        result = super().__call__(state)
        tool_msg = next((m for m in result["messages"] if isinstance(m, ToolMessage)), None)
        if tool_msg:
            try:
                output = json.loads(tool_msg.content)
                result["retrieved"] = output.get("retrieved", [])
            except:
                result["retrieved"] = []
        return result

tool_node = RetrievalEnrichedToolNode(tools)

# === State ===
class StrategistState(TypedDict):
    store_name: str
    city: str
    trends: dict
    entrance_side: str
    messages: Annotated[list, operator.add]
    retrieved: list
    draft_plan: dict
    review: dict
    final_plan: LayoutPlan
    iteration: int

# === Nodes ===

# @observe(name="RAG Node")
def rag_node(state: StrategistState):
    """Builds RAG query and triggers tool call."""
    if state.get("iteration", 0) == 0:
        query = (
            f"Blue Retail store layout constraints for {state['city']}: "
            "north wall, accessibility, fixture catalog, brand guidelines, "
            "decompression zone, aisle width, customer flow, leasing agreement"
        )
    else:
        issues = state["review"].get("issues", [])
        suggestions = state["review"].get("suggestions", [])
        problems = issues + suggestions
        query = (
            f"Fix layout issues in {state['city']}: {'; '.join(problems[:3])}"
            if problems
            else f"Improve best practices for {state['city']} store layout"
        )

    # Trigger tool call via LLM (ensures ToolNode runs)
    tool_call_prompt = f"""
You need more context. CALL `rag_tool` with:

Query: {query}
Top-K: 10

Respond **only** with a tool call.
"""
    response = llm.invoke([HumanMessage(content=tool_call_prompt)])

    if response.tool_calls:
        return {
            "messages": [response],
            "iteration": state.get("iteration", 0) + 1
        }
    else:
        # Fallback: force tool call
        from uuid import uuid4
        return {
            "messages": [AIMessage(
                content="",
                tool_calls=[{
                    "name": "rag_tool",
                    "args": {"query": query, "top_k": 10},
                    "id": str(uuid4()),
                    "type": "tool_call"
                }]
            )],
            "iteration": state.get("iteration", 0) + 1
        }

# @observe(name="Planner Node")
def planner_node(state: StrategistState):
    trends_summary = "\n".join([
        f"- {item['keyword']}: {item['score']}"
        for item in state["trends"].get("interest_over_time_national", [])[:3]
    ])
    context = "\n\n".join([c["text"] for c in state.get("retrieved", [])[:5]])

    prompt = PLANNER_PROMPT.format(
        store_name=state["store_name"],
        city=state["city"],
        entrance_side=state["entrance_side"],
        trends_summary=trends_summary,
        context=context,
        format_instructions=parser.get_format_instructions()
    )

    response = llm.invoke([HumanMessage(content=prompt)])

    try:
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("```", 2)[1]
            if content.lower().startswith("json"):
                content = content[4:].strip()

        data = json.loads(content)

        if "store_layout" in data:
            data = data["store_layout"]

        # Normalize dimensions
        dims = data.get("dimensions_m")
        if isinstance(dims, dict):
            data["dimensions_m"] = (dims.get("length", 20), dims.get("width", 12))
        elif isinstance(dims, (list, tuple)):
            data["dimensions_m"] = tuple(dims[:2])

        # Defaults
        data.setdefault("store_name", f"{state['store_name']} - {state['city']}")
        data.setdefault("city", state["city"])
        data.setdefault("zones", [])
        data.setdefault("compliance_notes", [])
        data.setdefault("best_practice_score", 0.0)

        plan = LayoutPlan(**data)
        return {
            "draft_plan": plan.model_dump(),
            "messages": [response]
        }
    except Exception as e:
        print(f"Planner parse error: {e}")
        print(f"Raw response: {response.content[:500]}")
        return {"messages": [response]}

# @observe(name="Reviewer Node")
def reviewer_node(state: StrategistState):
    context = "\n\n".join([c["text"] for c in state.get("retrieved", [])])
    prompt = REVIEWER_PROMPT.format(
        layout_json=json.dumps(state["draft_plan"], indent=2),
        context=context
    )
    response = llm.invoke([HumanMessage(content=prompt)])
    try:
        review = json.loads(response.content.strip().split("```")[0])
        return {"review": review, "messages": [AIMessage(content=f"Review: {review}")]}
    except:
        return {
            "review": {"is_compliant": False, "best_practice_score": 0},
            "messages": [response]
        }

# @observe(name="Decider Node")
def decider_node(state: StrategistState):
    review = state["review"]
    if review.get("is_compliant") and review.get("best_practice_score", 0) >= 8.5:
        plan = state["draft_plan"].copy()
        plan["best_practice_score"] = review["best_practice_score"]
        plan["compliance_notes"] = review.get("issues", []) + review.get("suggestions", [])
        return {"final_plan": LayoutPlan(**plan)}
    else:
        return {"messages": [AIMessage(content="Refining layout...")]}

# === Routing ===
def route(state: StrategistState):
    if state.get("final_plan"):
        return END
    if state.get("review", {}).get("is_compliant"):
        return END
    return "rag"

# === Build Subgraph ===
subgraph = StateGraph(StrategistState)
subgraph.add_node("rag", tool_node)
subgraph.add_node("planner", planner_node)
subgraph.add_node("reviewer", reviewer_node)
subgraph.add_node("decider", decider_node)

subgraph.set_entry_point("planner")
subgraph.add_edge("planner", "reviewer")
subgraph.add_edge("reviewer", "decider")
subgraph.add_conditional_edges("decider", route, {"rag": "rag", END: END})
subgraph.add_edge("rag", "planner")

strategist_subgraph = subgraph.compile()

# === Demo ===
if __name__ == '__main__':
    print("\nStarting Layout Strategist Subgraph Demo...\n")
    
    result = strategist_subgraph.invoke({
        "store_name": "Blue Retail Ventures",
        "city": "Surat",
        "entrance_side": "south",
        "trends": {
            "interest_over_time_national": [
                {"keyword": "iPhone 15", "score": 95},
                {"keyword": "gaming laptop", "score": 88},
                {"keyword": "noise cancelling headphones", "score": 72}
            ]
        },
        "messages": [],
        "iteration": 0
    })

    print("="*60)
    print("FINAL LAYOUT PLAN")
    print("="*60)
    print(json.dumps(result["final_plan"].model_dump(), indent=2))

    print("\n" + "="*60)
    print("REVIEW LOG")
    print("="*60)
    print(json.dumps(result.get("review", {}), indent=2))

    print("\n" + "="*60)
    print("RAG RETRIEVED CHUNKS (Last Call)")
    print("="*60)
    for i, chunk in enumerate(result.get("retrieved", [])[:3]):
        print(f"[{i+1}] {chunk['source']} (score: {chunk['score']:.3f})")
        print(f"    {chunk['text'][:200]}...\n")