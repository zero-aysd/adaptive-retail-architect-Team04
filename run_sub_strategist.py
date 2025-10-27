from app.agents.layout_strategist import strategist_subgraph
import json

    # === CONFIG ===
CITY = "Surat"
ENTRANCE = "south"
TRENDS = {
    "interest_over_time_national": [
        {"keyword": "iPhone 15", "score": 95},
        {"keyword": "gaming laptop", "score": 88},
        {"keyword": "noise cancelling headphones", "score": 72}
    ]
}
STORE_NAME="Blue Retail Stores"

# === RUN THE SUBGRAPH ===
print("Starting Layout Strategist (ReAct + Self-Critique)...\n")
state = {"store_name":STORE_NAME,
    "city": CITY,
    "trends": TRENDS,
    "entrance_side": ENTRANCE,
    "messages": [],
    "iteration": 0
}
result = strategist_subgraph.invoke(state)

# === PRETTY PRINT RESULTS ===
print("="*60)
print("FINAL LAYOUT PLAN")
print("="*60)
print(json.dumps(result["final_plan"].model_dump(), indent=2))

print("\n" + "="*60)
print("REVIEW LOG (Self-Critique)")
print("="*60)
if "review" in result:
    print(json.dumps(result["review"], indent=2))
else:
    print("No review log (direct approval)")

print("\n" + "="*60)
print("RAG RETRIEVED CHUNKS (Last Call)")
print("="*60)
retrieved = result.get("retrieved", [])
for i, chunk in enumerate(retrieved[:3]):
    print(f"[{i+1}] {chunk['source']} (score: {chunk['score']:.3f})")
    print(f"    {chunk['text'][:200]}...\n")