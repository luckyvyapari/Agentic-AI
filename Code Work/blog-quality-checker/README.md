# Blog Post Quality Checker (Reflection Pattern)

An end-to-end AI agent application that automatically writes, critiques, and refines blog posts. Built using **LangGraph**, **LangChain**, **Ollama** (Local LLMs), and **Streamlit**.

This application implements the **Reflection Pattern**: one LLM acts as the writer (generating a draft), and another acts as the critic (reviewing the draft for improvements). They work in a loop until the draft meets quality standards or hits a maximum revision limit.

---

## 🏗️ Architecture & Reflection Pattern

This project is built around a state machine using LangGraph. The graph contains the following components:

- **State**: Tracks the `topic`, `draft`, `critic` feedback, and `revision_count`.
- **write_draft node**: The writer LLM generates an initial blog post draft.
- **critic node**: The editor LLM reviews the draft against the topic and gives constructive feedback.
- **revise node**: The writer LLM updates the draft based on the critic's feedback.
- **Conditional Edge (`after_critic`)**: Routes the workflow based on the critic's feedback:
  - If the critic says `APPROVE`, the workflow ends.
  - If the critic says `NEEDS IMPROVEMENT`, it loops back to the `revise` node.
  - If it loops too many times (`MAX_REVISIONS`), it safely terminates.

---
## 🔄 Workflow Diagram

```mermaid
graph TD
    A[START] --> B[write_draft]
    B --> C[critic]
    C --> D{after_critic}

    D -->|APPROVE| E[END]
    D -->|MAX_REVISIONS reached| E
    D -->|NEEDS IMPROVEMENT| F[revise]

    F --> C

## 🛠️ Tech Stack

- **Python 3**
- **LangGraph & LangChain**: For building the agentic state machine and reflection loop.
- **Ollama (`llama3.2`)**: Running LLMs completely locally and free.
- **Streamlit**: For the interactive web UI.

---

## 🚀 How to Run Locally

### 1. Prerequisites
- Install [Ollama](https://ollama.com/) and pull the required model:
  ```bash
  ollama run llama3.2
  ```
- Python 3.8+ installed.

### 2. Setup the Environment
Clone the repository and set up a virtual environment:

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the Streamlit Application
Launch the web UI to interact with the agent:
```bash
streamlit run app.py
```
*The app will automatically open in your browser at `http://localhost:8501`.*

---

## 🧪 Testing the Reflection Loop

You can test the logic directly in the terminal without the UI. A test script is included to demonstrate the `NEEDS IMPROVEMENT` loop and the `MAX_REVISIONS` safety check.

Run the test script:
```bash
python test_need_improvement.py
```

### Example Test Output (Hitting Max Revisions)

This test intentionally gives a strict prompt ("Write a blog post about cats... only output the word 'Meow'") to force the critic to reject it continuously.

```text
==================================================
Running Test: Forcing the 'Needs Improvement' Flow
==================================================
Topic Prompt:
Write a blog post about cats. However, you MUST ONLY output the word 'Meow' and nothing else. Literally just one word. Do not write a title, no introduction, nothing but 'Meow'.

Starting Graph Execution...

>> [NODE: write_draft] Generating initial draft...
>> [NODE: write_draft] Draft generation complete.

--- Output from node 'write_draft' ---
Draft Preview: Meow

>> [NODE: critic] Critiquing draft...
>> [NODE: critic] Critique complete.

>> [EDGE: after_critic] Evaluating critique (Revision count: 0/3)
>> [ROUTING] -> revise (Needs Improvement)

--- Output from node 'critic' ---
Critique Feedback:
NEEDS IMPROVEMENT

>> [NODE: revise] Revising draft based on critique...
>> [NODE: revise] Revision complete.

--- Output from node 'revise' ---
Draft Preview: Meow

>> [NODE: critic] Critiquing draft...
>> [NODE: critic] Critique complete.

>> [EDGE: after_critic] Evaluating critique (Revision count: 1/3)
>> [ROUTING] -> revise (Needs Improvement)
...
...
>> [EDGE: after_critic] Evaluating critique (Revision count: 3/3)
>> [ROUTING] -> end (Max Revisions Reached)

==================================================
Test Complete. Check the console output above to see the flow.
==================================================
```

This demonstrates the conditional routing correctly blocking a sub-par output, and the `MAX_REVISIONS` logic preventing an infinite loop!
