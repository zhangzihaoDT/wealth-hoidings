import os
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timezone

from src.planning_agent import planner_agent, executor_agent_step

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./research.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, index=True)
    status = Column(String, default="Pending")
    result = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)

templates = Jinja2Templates(directory="templates")
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")


def run_agent_workflow(task_id: int, topic: str):
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return

        task.status = "Planning"
        db.commit()

        plan = planner_agent(topic)
        context = {"topic": topic}

        for step_info in plan:
            step_name = step_info["step"]
            task.status = f"Running: {step_name}"
            db.commit()

            context = executor_agent_step(step_name, context)

        task.status = "Completed"
        task.result = context.get("final_report", "No report generated.")
        db.commit()
    except Exception as e:
        db.rollback()
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = f"Error: {str(e)}"
            db.commit()
    finally:
        db.close()


def generate_report(task_id: int, topic: str):
    thread = threading.Thread(target=run_agent_workflow, args=(task_id, topic))
    thread.start()


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    db = SessionLocal()
    tasks = db.query(Task).order_by(Task.created_at.desc()).all()
    db.close()
    return templates.TemplateResponse(request, "index.html", {"tasks": tasks})


@app.post("/tasks")
async def create_task(topic: str = Form(...)):
    db = SessionLocal()
    new_task = Task(topic=topic, status="Pending")
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    generate_report(new_task.id, new_task.topic)

    db.close()
    return {"message": "Task started", "task_id": new_task.id}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("researcher:app", host="0.0.0.0", port=8000, reload=True)
