import streamlit as st
import os
import uuid
from agent import graph
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Multi-Agent Research Assistant", page_icon="🔬", layout="wide")

# Initialize session state
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "state" not in st.session_state:
    st.session_state.state = None
if "processing" not in st.session_state:
    st.session_state.processing = False

# Sidebar for configuration
with st.sidebar:
    st.title("Settings")
    st.info(f"Thread ID: {st.session_state.thread_id}")
    if st.button("Reset Session"):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.state = None
        st.rerun()

st.title("🔬 Multi-Agent Research Assistant")
st.markdown("Gather info, write reports, and critique with Human-in-the-Loop.")

# Input for the research question
question = st.text_input("What would you like me to research?", placeholder="e.g., Latest advances in LLM reasoning")

if st.button("Start Research") and question:
    st.session_state.processing = True
    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    
    with st.status("🔍 Researching and drafting...", expanded=True) as status:
        # Initial run
        st.write("Fetching web results...")
        graph.invoke({"question": question}, config=config)
        status.update(label="Research Complete! Needs Review.", state="complete")
    
    st.session_state.processing = False
    st.rerun()

# Check current state of the graph
config = {"configurable": {"thread_id": st.session_state.thread_id}}
state_values = graph.get_state(config).values

if state_values:
    st.divider()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📄 Draft Report")
        st.markdown(state_values.get("draft_report", "No draft yet."))
        
    with col2:
        st.subheader("⚖️ Critic Feedback")
        score = state_values.get("critic_score", 0)
        st.metric("Critic Score", f"{score}/10")
        st.markdown(state_values.get("critic_feedback", "No feedback yet."))

    # Human in the loop controls
    if not state_values.get("approved", False):
        st.divider()
        st.subheader("🧑‍💻 Human Review")
        
        human_notes = st.text_area("Revision Notes (Optional)", placeholder="Tell the writer what to change...")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Approve & Generate PDF", use_container_width=True):
                # Update state and resume
                graph.update_state(config, {"approved": True, "human_feedback": "None"}, as_node="human_review")
                graph.invoke(None, config=config)
                st.rerun()
                
        with c2:
            if st.button("🔄 Request Revision", use_container_width=True):
                # Update state and resume
                graph.update_state(config, {"approved": False, "human_feedback": human_notes}, as_node="human_review")
                graph.invoke(None, config=config)
                st.rerun()

    # Final Report / PDF Download
    if state_values.get("approved", False):
        st.success("✅ Report Approved!")
        pdf_path = "research_report.pdf"
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="📥 Download Research Report (PDF)",
                    data=f,
                    file_name="research_report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
