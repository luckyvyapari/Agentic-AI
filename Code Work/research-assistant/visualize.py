from agent import graph

def save_graph():
    try:
        # Generate Mermaid PNG
        png_data = graph.get_graph().draw_mermaid_png()
        with open("graph.png", "wb") as f:
            f.write(png_data)
        print("Graph visualization saved to graph.png")
    except Exception as e:
        # Fallback to Mermaid text
        mermaid_text = graph.get_graph().draw_mermaid()
        with open("graph_mermaid.txt", "w") as f:
            f.write(mermaid_text)
        print("Graph Mermaid text saved to graph_mermaid.txt")
        print(f"Visualization error: {e}")

if __name__ == "__main__":
    save_graph()
