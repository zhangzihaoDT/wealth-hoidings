import time
from .agents import research_agent, writer_agent, editor_agent

def planner_agent(topic: str) -> list:
    """Creates a plan of steps."""
    print(f"[Planner Agent] Planning workflow for: {topic}")
    time.sleep(1)
    return [
        {"step": "research", "status": "pending"},
        {"step": "write", "status": "pending"},
        {"step": "edit", "status": "pending"}
    ]

def executor_agent_step(step: str, context: dict) -> dict:
    """Executes a single step in the plan."""
    topic = context.get("topic", "")
    
    if step == "research":
        res = research_agent(topic)
        context["research_data"] = res
    elif step == "write":
        draft = writer_agent(context.get("research_data", ""))
        context["draft"] = draft
    elif step == "edit":
        final = editor_agent(context.get("draft", ""))
        context["final_report"] = final
        
    return context
