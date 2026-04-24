import time
import json

from .agents import research_agent, writer_agent, editor_agent
from .bom_agent import bom_agent

def planner_agent(topic: str) -> list:
    """Creates a plan of steps."""
    print(f"[Planner Agent] Planning workflow for: {topic}")
    time.sleep(1)
    topic = topic.strip()
    if topic.startswith("http://") or topic.startswith("https://"):
        return [{"step": "bom", "status": "pending"}]
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
    elif step == "bom":
        data = bom_agent(topic)
        context["bom_data"] = data
        context["final_report"] = json.dumps(data, ensure_ascii=False, indent=2)
    elif step == "write":
        draft = writer_agent(context.get("research_data", ""))
        context["draft"] = draft
    elif step == "edit":
        final = editor_agent(context.get("draft", ""))
        context["final_report"] = final
        
    return context
