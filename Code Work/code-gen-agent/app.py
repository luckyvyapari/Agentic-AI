import streamlit as st
import time
import os
import sqlite3
import pandas as pd
from agent import graph
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command

# Page Config
st.set_page_config(
    page_title="Agentic Studio | Next-Gen AI Coding",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PREMIUM WHITE THEME (Custom CSS) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&family=JetBrains+Mono&display=swap');

:root {
    --primary: #000000;
    --secondary: #6366F1;
    --background: #FFFFFF;
    --surface: #FAFAFA;
    --border: #F0F0F0;
    --text-main: #111111;
    --text-muted: #666666;
}

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
    background-color: var(--background) !important;
    color: var(--text-main);
}

.stApp {
    background-color: var(--background);
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border);
}

/* Card-like containers */
.stCard {
    background-color: var(--background);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    margin-bottom: 24px;
    transition: transform 0.2s ease;
}

.stCard:hover {
    box-shadow: 0 10px 20px rgba(0,0,0,0.03);
}

/* Custom Buttons */
.stButton>button {
    background-color: var(--primary) !important;
    color: white !important;
    border-radius: 10px !important;
    border: none !important;
    padding: 12px 24px !important;
    font-weight: 600 !important;
    width: 100%;
    transition: all 0.3s ease !important;
}

.stButton>button:hover {
    background-color: #333333 !important;
    transform: translateY(-2px);
}

/* Secondary/Outline Button */
div[data-testid="stHorizontalBlock"] div.stButton>button {
    background-color: white !important;
    color: black !important;
    border: 1px solid #DDDDDD !important;
}

/* Log Container */
.log-container {
    background-color: #F9FAFB;
    border-radius: 12px;
    padding: 16px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    height: 500px;
    overflow-y: auto;
    border: 1px solid var(--border);
}

.log-entry {
    padding: 8px 0;
    border-bottom: 1px solid #F0F2F5;
    display: flex;
    gap: 12px;
}

.log-time { color: #A0AEC0; flex-shrink: 0; }
.log-node { font-weight: 600; color: #4A5568; width: 100px; flex-shrink: 0; }
.log-status { color: #2D3748; }

/* Step Indicator */
.step-box {
    display: flex;
    justify-content: space-between;
    margin-bottom: 30px;
    position: relative;
}
.step-item {
    text-align: center;
    z-index: 1;
    width: 20%;
}
.step-circle {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: #F3F4F6;
    border: 2px solid #E5E7EB;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 8px;
    font-weight: bold;
    color: #9CA3AF;
    transition: all 0.3s ease;
}
.step-active .step-circle {
    background: #000000;
    border-color: #000000;
    color: white;
    box-shadow: 0 0 15px rgba(0,0,0,0.1);
}
.step-line {
    position: absolute;
    top: 20px;
    left: 10%;
    right: 10%;
    height: 2px;
    background: #E5E7EB;
    z-index: 0;
}

/* Code Editor Overrides */
.stTextArea textarea {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.9rem !important;
    border-radius: 10px !important;
    border: 1px solid var(--border) !important;
}
</style>
""", unsafe_allow_html=True)

# --- STATE MANAGEMENT ---
if "thread_id" not in st.session_state:
    st.session_state.thread_id = f"st_{int(time.time())}"
if "running" not in st.session_state:
    st.session_state.running = False
if "current_state" not in st.session_state:
    st.session_state.current_state = None

def get_history():
    conn = sqlite3.connect("agent_history.db")
    df = pd.read_sql_query(
        "SELECT * FROM logs WHERE thread_id = ? ORDER BY id DESC", 
        conn, 
        params=(st.session_state.thread_id,)
    )
    conn.close()
    return df

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='margin-bottom:0;'>Studio</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#888; font-size:0.8rem;'>Session: " + st.session_state.thread_id + "</p>", unsafe_allow_html=True)
    
    if st.button("New Project"):
        st.session_state.thread_id = f"st_{int(time.time())}"
        st.session_state.running = False
        st.session_state.current_state = None
        st.rerun()

    st.divider()
    st.markdown("### Streaming Logs")
    history_df = get_history()
    
    log_html = '<div class="log-container">'
    for _, row in history_df.iterrows():
        t = row['timestamp'].split(' ')[1]
        log_html += f'<div class="log-entry"><span class="log-time">{t}</span><span class="log-node">{row["node_name"]}</span><span class="log-status">{row["status"]}</span></div>'
    log_html += '</div>'
    st.markdown(log_html, unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<div style="display: flex; align-items: center; gap: 15px; margin-bottom: 40px;"><div style="background: black; color: white; padding: 10px; border-radius: 12px; font-weight: bold; font-size: 1.5rem;">AS</div><div><h1 style="margin:0; letter-spacing: -1.5px;">Agentic Studio</h1><p style="margin:0; color: #888;">Premium Multi-Agent AI Software Engineering</p></div></div>', unsafe_allow_html=True)

# --- STEP INDICATOR ---
nodes = ["CODER", "CRITIC", "HUMAN", "TESTER", "DEPLOY"]
current_node_name = "CODER" # Default
if st.session_state.current_state:
    # Estimate current node from history
    last_log = history_df.iloc[0] if not history_df.empty else None
    if last_log is not None:
        current_node_name = last_log['node_name'].replace("_REVIEW", "")

step_html = '<div class="step-box"><div class="step-line"></div>'
for i, n in enumerate(nodes):
    is_active = "step-active" if current_node_name in n else ""
    step_html += f'<div class="step-item {is_active}"><div class="step-circle">{i+1}</div><div style="font-size: 0.7rem; font-weight: 600; color: {"#000" if is_active else "#AAA"}">{n}</div></div>'
step_html += '</div>'
st.markdown(step_html, unsafe_allow_html=True)

# --- MAIN LAYOUT ---
col_left, col_right = st.columns([1, 1.2], gap="large")

with col_left:
    st.markdown('<div class="stCard">', unsafe_allow_html=True)
    st.markdown("### Build Specification")
    prompt = st.text_area("What are we building today?", placeholder="e.g. A web scraper for financial news that stores data in SQLite...", height=180)
    file_name = st.text_input("Entrypoint Name", value="main_module")
    
    if st.button("Initialize Agent", disabled=st.session_state.running):
        st.session_state.running = True
        config = {"configurable": {"thread_id": st.session_state.thread_id}}
        
        initial_input = {
            "request": prompt,
            "file_name": file_name,
            "iteration": 0,
            "logs": [f"Session initialized."]
        }
        
        for event in graph.stream(initial_input, config=config, stream_mode="values"):
            st.session_state.current_state = event
            
        st.session_state.running = False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # --- HUMAN REVIEW INTERFACE ---
    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    state = graph.get_state(config)

    if state.next and state.next[0] == "human_review":
        st.markdown('<div class="stCard" style="border: 1px solid #000;">', unsafe_allow_html=True)
        st.markdown("### 🚦 Human Intervention Required")
        
        interrupt_data = state.tasks[0].interrupts[0].value
        
        tabs = st.tabs(["Draft Analysis", "Criticism"])
        with tabs[0]:
            edited_code = st.text_area("Code Workspace", value=interrupt_data['code'], height=350)
        with tabs[1]:
            st.markdown(f"**Critic Feedback:**\n{interrupt_data.get('critic_feedback', 'No feedback.')}")
        
        feedback = st.text_input("Review Notes / Directives")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Approve & Finalize"):
                resume_cmd = Command(resume={"action": "approve", "code": edited_code, "feedback": feedback})
                for event in graph.stream(resume_cmd, config=config, stream_mode="values"):
                    st.session_state.current_state = event
                st.rerun()
        with c2:
            if st.button("Reject & Revise"):
                resume_cmd = Command(resume={"action": "feedback", "code": edited_code, "feedback": feedback})
                for event in graph.stream(resume_cmd, config=config, stream_mode="values"):
                    st.session_state.current_state = event
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    if st.session_state.current_state:
        s = st.session_state.current_state
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        st.markdown("### Workspace Output")
        
        res_tabs = st.tabs(["✨ Code", "🧪 Tests", "📜 Execution Trace"])
        
        with res_tabs[0]:
            if s.get("code"):
                st.code(s["code"], language="python")
            else:
                st.info("Awaiting code generation...")
        
        with res_tabs[1]:
            if s.get("test_results"):
                st.markdown(f"```text\n{s['test_results']}\n```")
            else:
                st.info("Tests pending code approval.")
                
        with res_tabs[2]:
            for log in reversed(s.get("logs", [])):
                st.markdown(f"• {log}")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- VISUAL TRACE ---
    st.markdown("### Decision Trace")
    if not history_df.empty:
        for _, row in history_df.iterrows():
            with st.expander(f"{row['node_name']} - {row['status']} (Iter {row['iteration']})"):
                st.json(row['data'])
    else:
        st.info("Graph hasn't started yet.")

