from agent import graph

def test_blog_graph():
    topic = "The Role of AI in Modern Education"
    print(f"Testing Blog Quality Checker with topic: '{topic}'\n")
    
    initial_state = {"topic": topic, "draft": "", "critic": "", "revision_count": 0}
    
    for output in graph.stream(initial_state):
        for key, value in output.items():
            print(f"--- Completed Node: {key} ---")
            if key == "write_draft":
                print(f"Draft Snippet: {value['draft'][:200]}...\n")
            elif key == "critic":
                print(f"Critic Feedback: {value['critic']}\n")
            elif key == "revise":
                print(f"Revised Draft Snippet: {value['draft'][:200]}...\n")

    print("\n--- Process Complete ---")

if __name__ == "__main__":
    test_blog_graph()
