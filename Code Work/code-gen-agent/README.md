# Python Code Generator Agent (Reflection Pattern)

This project implements a Multi-Agent system using **LangGraph** and **Ollama** that generates Python code, allows for human-in-the-loop review/editing, automatically creates unit tests, and deploys the final system.

## Workflow
1. **Coder Agent**: Writes the initial Python code based on your prompt.
2. **Human Review**: The graph **interrupts** and waits for your input.
   - Type `approve` to move to testing.
   - Enter feedback (e.g., "add a method for subtraction") to trigger a revision.
3. **Tester Agent**: Once approved, this agent writes `unittest` cases.
4. **Deployer**: Saves the code and tests into the `deployed_system/` folder.

## Setup
1. Ensure you have **Ollama** running with the `llama3.2` model (or update `agent.py` to your model).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
### 1. Interactive CLI
Run the terminal-based interface:
```bash
python test.py
```

### 2. Modern Web UI
Run the Streamlit dashboard:
```bash
streamlit run app.py
```

## Project Structure
- `agent.py`: The LangGraph state machine definition.
- `app.py`: Streamlit Web Dashboard.
- `test.py`: Interactive CLI for human-in-the-loop.
- `deployed_system/`: (Generated) Final output folder.
