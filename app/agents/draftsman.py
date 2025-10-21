import matplotlib.pyplot as plt
import io
import base64
from typing import Dict, Any

def generate_diagram(plan: Dict[str, Any]) -> str:
    """
    AI Draftsman: Convert JSON plan to 2D PNG diagram.
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 15)
    ax.set_aspect('equal')
    
    # Draw zones (mock rectangles)
    colors = ['lightblue', 'lightgreen', 'lightcoral']
    for i, zone in enumerate(plan['zones']):
        x, y, w, h = 2 + i*5, 2, 4, 3  # Mock positions
        ax.add_patch(plt.Rectangle((x, y), w, h, fill=True, color=colors[i % len(colors)], alpha=0.5))
        ax.text(x + w/2, y + h/2, zone['name'], ha='center', va='center')
    
    ax.set_title('Conceptual Retail Layout')
    ax.axis('off')
    
    # Save to base64 for API response
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    
    return f"data:image/png;base64,{img_base64}"