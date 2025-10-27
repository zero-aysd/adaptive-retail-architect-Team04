# app/agents/draftsman.py
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path
from typing import Dict
from app.schemas.layout import LayoutPlan  # ← Import Pydantic model

ARTIFACT_DIR = Path("artifacts")
ARTIFACT_DIR.mkdir(exist_ok=True)

def draftsman_node(state: Dict) -> Dict:
    """
    Converts LayoutPlan (Pydantic model) → 2D PNG diagram.
    """
    # === 1. Reconstruct Pydantic model from dict ===
    plan_dict = state["final_plan"]
    try:
        plan = LayoutPlan(**plan_dict)  # ← This gives you .dimensions_m, .zones, etc.
    except Exception as e:
        raise ValueError(f"Invalid layout plan: {e}") from e

    city = state["city"]
    output_path = ARTIFACT_DIR / f"layout_{city.lower()}.png"

    # === 2. Plotting ===
    fig, ax = plt.subplots(1, figsize=(12, 8))
    ax.set_xlim(0, plan.dimensions_m[0])
    ax.set_ylim(0, plan.dimensions_m[1])
    ax.set_aspect('equal')
    ax.set_title(f"{plan.store_name} - {plan.city}\nAdaptive Retail Layout", fontsize=14, pad=20)
    ax.set_xlabel("Length (m)")
    ax.set_ylabel("Width (m)")

    # Color palette
    colors = plt.cm.Set3.colors

    for i, zone in enumerate(plan.zones):
        color = colors[i % len(colors)]
        rect = patches.Rectangle(
            (zone.x, zone.y), zone.width, zone.height,
            linewidth=2, edgecolor='black', facecolor=color, alpha=0.7,
            label=zone.name
        )
        ax.add_patch(rect)

        # Zone label
        products = ', '.join(zone.products[:2]) if zone.products else "Empty"
        ax.text(
            zone.x + zone.width / 2,
            zone.y + zone.height / 2,
            f"{zone.name}\n{products}",
            ha='center', va='center', fontsize=9, fontweight='bold',
            color='black',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8)
        )

    # Entrance arrow
    entrance_map = {
        "south": (plan.dimensions_m[0] / 2, 0),
        "north": (plan.dimensions_m[0] / 2, plan.dimensions_m[1]),
        "east": (plan.dimensions_m[0], plan.dimensions_m[1] / 2),
        "west": (0, plan.dimensions_m[1] / 2)
    }
    ex, ey = entrance_map[plan.entrance_side]

    offset = 2
    tx = ex + (offset if plan.entrance_side == "west" else -offset if plan.entrance_side == "east" else 0)
    ty = ey + (offset if plan.entrance_side == "south" else -offset if plan.entrance_side == "north" else 0)

    ax.annotate(
        "ENTRANCE",
        xy=(ex, ey),
        xytext=(tx, ty),
        arrowprops=dict(arrowstyle="->", lw=2, color='red'),
        fontsize=12, fontweight='bold', color='red',
        ha='center', va='center'
    )

    # Legend
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc='upper left', bbox_to_anchor=(1, 1))

    # Compliance notes
    if plan.compliance_notes:
        notes = "\n".join(plan.compliance_notes[:3])
        ax.text(0.02, 0.98, f"Compliance: {notes}", transform=ax.transAxes,
                fontsize=8, verticalalignment='top',
                bbox=dict(boxstyle="round", facecolor="lightgreen", alpha=0.9))

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close(fig)

    print(f"Layout diagram saved: {output_path.resolve()}")

    return {
        "diagram_path": str(output_path.resolve()),
        "messages": [f"Diagram generated: {output_path.name}"]
    }