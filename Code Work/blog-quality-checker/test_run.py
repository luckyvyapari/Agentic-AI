from agent import graph

if __name__ == "__main__":
    initial_state = {"topic": "The future of AI in coding", "draft": "", "critic": "", "revision_count": 0}
    print("Starting stream...")
    for output in graph.stream(initial_state):
        for key, value in output.items():
            print(f"--- Node: {key} ---")
            if key == "write_draft":
                print("Draft preview:", value.get("draft")[:100], "...")
            elif key == "critic":
                print("Critic preview:", value.get("critic")[:100], "...")
            elif key == "revise":
                print("Revise preview:", value.get("draft")[:100], "...")
    print("Done!")
