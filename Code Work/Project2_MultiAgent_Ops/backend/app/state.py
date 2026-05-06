from typing import Annotated, Sequence, TypedDict, List, Optional
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    # The messages in the conversation
    messages: Annotated[Sequence[BaseMessage], operator.add]
    # The next agent to act (always take the latest value)
    next: Annotated[str, lambda x, y: y]
    # Audit logs
    logs: Annotated[List[dict], operator.add]
    # Pending approval
    pending_tool_call: Annotated[Optional[dict], lambda x, y: y]
    # Approval status
    approved: Annotated[bool, lambda x, y: y]
