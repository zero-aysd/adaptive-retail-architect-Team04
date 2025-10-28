# graph.py
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
import operator
from app.agents.market_analyst import run_market_analyst
from app.agents.geo_resolver import resolve_geo
from app.agents.layout_strategist import strategist_subgraph
from app.agents.draftsman import draftsman_node
from app.utils import load_env_file
import os
import json
from datetime import datetime
from langfuse import observe, get_client
from langfuse.langchain import CallbackHandler as LBHandler

# === Load Env ===
load_env_file()

langfuse = get_client()
 
# Verify connection
if langfuse.auth_check():
    print("Langfuse client is authenticated and ready!")
else:
    print("Authentication failed. Please check your credentials and host.")

langfuse_handler = LBHandler()

# === Main State ===
class MainState(TypedDict):
    store_name: str
    city: str
    keywords: list[str]
    entrance_side: str
    messages: Annotated[list, operator.add]
    market_trends: dict
    final_plan: dict
    diagram_path: str
    review_log: dict

# === Helper: Pretty Print with Timestamp ===
def log_agent(name: str, message: str, data: dict = None):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n[{timestamp}] AGENT: {name.upper()}")
    print(f"{'─' * 60}")
    print(message)
    if data:
        print("Payload:")
        print(json.dumps(data, indent=2)[:500] + ("..." if len(json.dumps(data, indent=2)) > 500 else ""))
    print(f"{'─' * 60}\n")

# === Nodes ===

def market_analyst_node(state: MainState):
    log_agent("market_analyst", f"Analyzing trends for {state['city']}...", {
        "keywords": state["keywords"],
        "entrance": state["entrance_side"]
    })

    geo = resolve_geo(state["city"])
    log_agent("market_analyst", "Geo resolved", geo)

    result = run_market_analyst(
        keywords=state["keywords"],
        geo=geo["geo"],
        sub_geo=geo["sub_geo"],
        
    )

    trends_count = len(result["payload"]["signals"]["interest_over_time_national"])
    log_agent("market_analyst", f"Analysis complete", {
        "top_trends": result["payload"]["signals"]["interest_over_time_national"][:3],
        "total_signals": trends_count
    })

    return {
        "market_trends": result,
        "messages": [f"Market analysis done. {trends_count} trends found."]
    }

def strategist_node(state: MainState):
    trends = state["market_trends"]["payload"]["signals"]["interest_over_time_national"][:3]
    log_agent("layout_strategist", f"Designing layout for {state['city']}...", {
        "store": state["store_name"],
        "entrance": state["entrance_side"],
        "top_3_trends": [f"{t['keyword']} ({t['score']})" for t in trends]
    })

    result = strategist_subgraph.invoke({
        "store_name": state["store_name"],
        "city": state["city"],
        "trends": state["market_trends"]["payload"]["signals"],
        "entrance_side": state["entrance_side"],
        "messages": [],
        "iteration": 0
    })

    plan = result["final_plan"]
    review = result.get("review", {})
    log_agent("layout_strategist", "Layout designed", {
        "zones": len(plan.zones),
        "best_practice_score": plan.best_practice_score,
        "is_compliant": review.get("is_compliant", False),
        "issues": review.get("issues", []),
        "suggestions": review.get("suggestions", [])
    })

    return {
        "final_plan": plan.model_dump(),
        "review_log": review,
        "messages": result.get("messages", [])
    }

def draftsman_node_wrapper(state: MainState):
    log_agent("draftsman", f"Generating diagram for {state['city']}...")
    output = draftsman_node(state)
    log_agent("draftsman", "Diagram saved", {
        "path": output["diagram_path"]
    })
    return output

def create_graph():
    # === Build Graph ===
    graph = StateGraph(MainState)

    graph.add_node("market", market_analyst_node)
    graph.add_node("strategist", strategist_node)
    graph.add_node("draftsman", draftsman_node_wrapper)

    graph.set_entry_point("market")
    graph.add_edge("market", "strategist")
    graph.add_edge("strategist", "draftsman")
    graph.add_edge("draftsman", END)

    return graph.compile().with_config({"callbacks":[langfuse_handler]})



# === Demo ===
if __name__ == '__main__':
    print("STARTING FULL RETAIL LAYOUT COPILOT")
    print("=" * 80)
    app = create_graph()
    result = app.invoke({
        "store_name": "Blue Retail Ventures",
        "city": "Surat",
        "keywords": ["iPhone 15", "gaming laptop"],
        "entrance_side": "south",
        "messages": [],
    })

    print("\n" + "FINAL OUTPUT SUMMARY".center(70, "="))
    print(f"Store: {result['final_plan']['store_name']}")
    print(f"City: {result['final_plan']['city']}")
    print(f"Best Practice Score: {result['final_plan']['best_practice_score']:.1f}/10")
    print(f"Compliance Notes: {len(result['final_plan']['compliance_notes'])}")
    print(f"Diagram: {result['diagram_path']}")

    print("\nTop 3 Trending Products:")
    trends = result["market_trends"]["payload"]["signals"]["interest_over_time_national"]
    for item in trends[:3]:
        print(f"  • {item['keyword']} (score: {item['score']})")

    print(f"\nOpen file: {result['diagram_path']}")