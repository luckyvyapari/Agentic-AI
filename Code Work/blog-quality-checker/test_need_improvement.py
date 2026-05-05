import os
from agent import graph

def test_needs_improvement():
    # A highly constrained prompt that usually fails on the first try,
    # triggering the 'NEEDS IMPROVEMENT' condition from the critic node.
    # complex_topic = (
    #     "Write a blog post about cats. "
    #     "However, you MUST ONLY output the word 'Meow' and nothing else. "
    #     "Literally just one word. Do not write a title, no introduction, nothing but 'Meow'."
    # )

    complex_topic = (
        "Write a blog post about cats. "
    )
    
    
    print("==================================================")
    print("Running Test: Forcing the 'Needs Improvement' Flow")
    print("==================================================")
    print(f"Topic Prompt:\n{complex_topic}\n")
    print("Starting Graph Execution...")
    
    # Initialize the state
    initial_state = {"topic": complex_topic, "draft": "", "critic": "", "revision_count": 0}
    
    # Run the graph and stream the state updates to see the flow clearly
    for output in graph.stream(initial_state):
        # 'output' is a dictionary where the key is the node name that just ran
        for key, value in output.items():
            print(f"\n--- Output from node '{key}' ---")
            
            if "draft" in value and key in ["write_draft", "revise"]:
                # Print a snippet of the draft to keep the log readable
                draft_preview = value["draft"][:150] + "..." if len(value["draft"]) > 150 else value["draft"]
                print(f"Draft Preview: {draft_preview}")
                
            if "critic" in value and key == "critic":
                print(f"Critique Feedback:\n{value['critic']}")

    print("\n==================================================")
    print("Test Complete. Check the console output above to see the flow.")
    print("==================================================")

if __name__ == "__main__":
    test_needs_improvement()
