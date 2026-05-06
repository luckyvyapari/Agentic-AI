from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from typing import List, Optional
from app.workflow import app as graph_app
from langchain_core.messages import HumanMessage
import uuid

app = FastAPI(title="Multi-Agent Ops API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



from pydantic import Field

class QueryRequest(BaseModel):
    query: str
    thread_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))

class ApprovalRequest(BaseModel):
    thread_id: str
    approve: bool

@app.post("/run")
async def run_workflow(request: QueryRequest):
    config = {"configurable": {"thread_id": request.thread_id}}
    
    # Start the workflow
    initial_state = {
        "messages": [HumanMessage(content=request.query)],
        "logs": [],
        "approved": False
    }
    
    # Run until interrupt or completion
    final_state = graph_app.invoke(initial_state, config=config)
    
    # Format output
    return {
        "thread_id": request.thread_id,
        "next": final_state.get("next"),
        "pending_approval": final_state.get("pending_tool_call"),
        "messages": [m.content for m in final_state["messages"]],
        "logs": final_state["logs"]
    }

@app.post("/approve")
async def approve_action(request: ApprovalRequest):
    config = {"configurable": {"thread_id": request.thread_id}}
    
    # Update state with approval
    graph_app.update_state(config, {"approved": request.approve, "pending_tool_call": None})
    
    # Resume workflow
    final_state = graph_app.invoke(None, config=config)
    
    return {
        "status": "Resumed",
        "messages": [m.content for m in final_state["messages"]],
        "logs": final_state["logs"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)

