import streamlit as st
from agent import graph

st.set_page_config(
    page_title="Blog Post Quality Checker",
    page_icon="✍️",
    layout="wide"
)

st.title("✍️ Blog Post Quality Checker")
st.markdown("This app uses a **Reflection Pattern** with two LLMs: one writes the draft, and the other critiques and improves it until it meets quality standards (or reaches the max revision limit).")

topic = st.text_input("Enter a Blog Topic:", placeholder="e.g. The Future of AI in Healthcare")

if st.button("Generate Blog Post", type="primary"):
    if not topic.strip():
        st.warning("Please enter a valid topic.")
    else:
        st.info("Starting the blog generation process...")
        
        # We will use Streamlit expanders to show the intermediate steps
        status_placeholder = st.empty()
        
        with st.status("Generating and Reviewing...", expanded=True) as status:
            initial_state = {"topic": topic, "draft": "", "critic": "", "revision_count": 0}
            
            final_state = initial_state.copy()
            step_count = 1
            
            # Use streaming to show the progress
            for output in graph.stream(initial_state):
                for key, value in output.items():
                    final_state.update(value)
                    
                    if key == "write_draft":
                        st.write(f"**Step {step_count}: Writing Initial Draft...**")
                        with st.expander("View Initial Draft"):
                            st.write(value.get("draft", ""))
                    elif key == "critic":
                        st.write(f"**Step {step_count}: Critiquing Draft...**")
                        with st.expander("View Critic Feedback"):
                            st.markdown(value.get("critic", ""))
                    elif key == "revise":
                        st.write(f"**Step {step_count}: Revising Draft based on feedback...**")
                        with st.expander("View Revised Draft"):
                            st.write(value.get("draft", ""))
                    
                    step_count += 1
            
            status.update(label="Process Complete!", state="complete", expanded=False)
        
        st.success("Blog Post Generation Complete!")
        
        st.subheader("Final Blog Post")
        if final_state and "draft" in final_state:
            st.markdown(final_state["draft"])
        else:
            st.error("Failed to generate the blog post.")
