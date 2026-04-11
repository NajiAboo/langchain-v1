from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from langgraph.types import Command

from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv
load_dotenv()


from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import MemorySaver

def delete_name_tool(name: str):
    """ mock function to delete customer record from customer table based on the name"""
    query = f'delete from customer where name= {name}'
    return query

def send_email(email_id: str, content: str):
    """Mock function to send email"""
    print(content)
    return content

def read_email(email_address: str):
    """ mock email to read the email"""
    return "successfully read the email"

checkpointer = MemorySaver()

agent = create_agent(
    model='gpt-4o-mini',
    tools=[delete_name_tool, send_email, read_email],
    checkpointer= checkpointer,
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "send_email": {
                    "allowed_decisions": ["approve", "reject",'edit'],
                    "description": "Please review the  content  before sending email"
                },
                "delete_name_tool": {
                    "allowed_decisions": ["approve", "reject"],
                    "description": """Please review the following SQL command before execution :
                    """
                },
                "read_email": False
                
            },
            description_prefix="Tool execution pending for approval"
        )
    ]
)
# ... (Import your existing tools and agent setup here) ...

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8001"], # Allow your specific frontend origin
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    thread_id: str

class DecisionRequest(BaseModel):
    thread_id: str
    decision_type: str  # approve, reject, edit
    edited_args: Optional[Dict] = None

@app.post("/chat")
async def chat(request: ChatRequest):
    config = {"configurable": {"thread_id": request.thread_id}}
    result = agent.invoke(
        {"messages": [{"role": "user", "content": request.message}]},
        config=config, version="v2"
    )
    return format_response(result)

@app.post("/decide")
async def decide(request: DecisionRequest):
    config = {"configurable": {"thread_id": request.thread_id}}
    
    # Construct the resume command
    if request.decision_type == "edit":
        # Note: In a real app, you'd fetch the tool name from the current state
        # For simplicity, we assume the frontend sends the full edited object
        resume_payload = {
            "decisions": [{
                "type": "edit",
                "edited_action": request.edited_args # Should contain name and args
            }]
        }
    else:
        resume_payload = {"decisions": [{"type": request.decision_type}]}

    result = agent.invoke(Command(resume=resume_payload), config=config, version="v2")
    return format_response(result)

def format_response(result):
    """Parses LangGraph result into a Frontend-friendly format"""
    if result.interrupts:
        interrupt = result.interrupts[0]
        action = interrupt.value['action_requests'][0]
        return {
            "status": "REQUIRES_ACTION",
            "tool_name": action['name'],
            "args": action['args'],
            "options": interrupt.value['review_configs'][0]['allowed_decisions'],
            "message": "Human intervention required."
        }
    
    last_msg = result.value['messages'][-1]
    return {
        "status": "COMPLETED",
        "message": last_msg.content,
        "history": [m.content for m in result.value['messages'] if m.type == 'human' or m.type == 'ai']
    }