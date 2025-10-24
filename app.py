import streamlit as st
import requests
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import threading
import re
from typing import Optional, List, Dict
from dotenv import load_dotenv


load_dotenv()
fastapi_app = FastAPI()

# CORS middleware
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
API_BASE_URL = "https://one-list-api.herokuapp.com"
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "illustriousvoyage")

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    intent: str
    success: bool
# Intent identification patterns
INTENT_PATTERNS = {
    "add_task": [
        r"add\s+(?:a\s+)?(?:new\s+)?task\s+(?:to\s+)?(.+)",
        r"create\s+(?:a\s+)?(?:new\s+)?task\s+(?:to\s+)?(.+)",
        r"new\s+task[:\s]+(.+)",
        r"remind\s+me\s+to\s+(.+)",
    ],
    "list_tasks": [
        r"(?:show|list|view|display|get)\s+(?:all\s+)?(?:my\s+)?tasks?",
        r"what\s+(?:are\s+)?(?:my\s+)?tasks?",
        r"show\s+me\s+(?:my\s+)?(?:all\s+)?tasks?",
    ],
    "list_incomplete": [
        r"(?:show|list|view|what)\s+.*(?:incomplete|pending|unfinished|undone)",
        r"(?:incomplete|pending|unfinished|undone)\s+tasks?",
    ],
    "list_complete": [
        r"(?:show|list|view|what)\s+.*(?:complete|completed|done|finished)",
        r"(?:complete|completed|done|finished)\s+tasks?",
    ],
    "view_task": [
        r"(?:show|view|display|get)\s+task\s+(?:number\s+)?(\d+)",
        r"task\s+(?:number\s+)?(\d+)",
    ],
    "complete_task": [
        r"(?:mark|set|complete|finish)\s+(?:task\s+)?['\"]?(.+?)['\"]?\s+(?:as\s+)?(?:done|complete|completed|finished)",
        r"(?:done|complete|finish)\s+(?:task\s+)?['\"]?(.+?)['\"]?",
        r"complete\s+task\s+(\d+)",
    ],
    "delete_task": [
        r"delete\s+(?:task\s+)?['\"]?(.+?)['\"]?",
        r"remove\s+(?:task\s+)?['\"]?(.+?)['\"]?",
    ],
}
def identify_intent(message: str) -> tuple:
    message = message.lower().strip()
    for intent, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                params = match.groups() if match.groups() else None
                return intent, params
    return "unknown", None

def get_all_tasks(token: str) -> List[Dict]:
    try:
        response = requests.get(
            f"{API_BASE_URL}/items",
            params={"access_token": token}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch tasks: {str(e)}")

def find_task_by_name(tasks: List[Dict], name: str) -> Optional[Dict]:
    name = name.lower().strip().strip('"\'')
    for task in tasks:
        if name in task.get("text", "").lower():
            return task
    return None

@fastapi_app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not ACCESS_TOKEN:
        return ChatResponse(
            response="Please configure your ACCESS_TOKEN to use this service.",
            intent="error",
            success=False
        )
    
    intent, params = identify_intent(request.message)
    
    try:
        if intent == "add_task":
            task_name = params[0].strip() if params else None
            if not task_name:
                return ChatResponse(response="Please specify a task name.", intent=intent, success=False)
            
            response = requests.post(f"{API_BASE_URL}/items", params={"access_token": ACCESS_TOKEN}, json={"text": task_name})
            response.raise_for_status()
            task = response.json()
            return ChatResponse(response=f"Task created: \"{task['text']}\"", intent=intent, success=True)
        
        elif intent == "list_tasks":
            tasks = get_all_tasks(ACCESS_TOKEN)
            if not tasks:
                return ChatResponse(response="You have no tasks.", intent=intent, success=True)
            
            task_list = "\n".join([f"{i+1}. {'✓' if t.get('complete') else '○'} {t['text']}" for i, t in enumerate(tasks)])
            return ChatResponse(response=f"You have {len(tasks)} task(s):\n\n{task_list}", intent=intent, success=True)
        
        elif intent == "list_incomplete":
            tasks = get_all_tasks(ACCESS_TOKEN)
            incomplete = [t for t in tasks if not t.get("complete")]
            
            if not incomplete:
                return ChatResponse(
                    response="You have no incomplete tasks. Great job!",
                    intent=intent,
                    success=True
                )
            
            task_list = "\n".join([
                f"{i+1}. {t['text']}"
                for i, t in enumerate(incomplete)
            ])
            return ChatResponse(
                response=f"You have {len(incomplete)} incomplete task(s):\n\n{task_list}",
                intent=intent,
                success=True
            )
        
        elif intent == "list_complete":
            tasks = get_all_tasks(ACCESS_TOKEN)
            complete = [t for t in tasks if t.get("complete")]
            
            if not complete:
                return ChatResponse(
                    response="You have no completed tasks yet.",
                    intent=intent,
                    success=True
                )
            
            task_list = "\n".join([
                f"{i+1}. {t['text']}"
                for i, t in enumerate(complete)
            ])
            return ChatResponse(
                response=f"You have {len(complete)} completed task(s):\n\n{task_list}",
                intent=intent,
                success=True
            )
        
        elif intent == "view_task":
            task_id = params[0] if params else None
            if not task_id:
                return ChatResponse(
                    response="Please specify a task number.",
                    intent=intent,
                    success=False
                )
            
            response = requests.get(
                f"{API_BASE_URL}/items/{task_id}",
                params={"access_token": ACCESS_TOKEN}
            )
            response.raise_for_status()
            task = response.json()
            
            status = "✓ Completed" if task.get("complete") else "○ Incomplete"
            return ChatResponse(
                response=f"Task #{task_id}:\n\nName: {task['text']}\nStatus: {status}",
                intent=intent,
                success=True
            )
        
        elif intent == "complete_task":
            task_identifier = params[0].strip() if params else None
            if not task_identifier:
                return ChatResponse(
                    response="Please specify which task to complete.",
                    intent=intent,
                    success=False
                )
            
            # Check if it's a task ID (number) or name
            if task_identifier.isdigit():
                task_id = task_identifier
            else:
                # Find task by name
                tasks = get_all_tasks(ACCESS_TOKEN)
                task = find_task_by_name(tasks, task_identifier)
                if not task:
                    return ChatResponse(
                        response=f"Task '{task_identifier}' not found.",
                        intent=intent,
                        success=False
                    )
                task_id = task["id"]
            
            response = requests.put(
                f"{API_BASE_URL}/items/{task_id}",
                params={"access_token": ACCESS_TOKEN},
                json={"complete": True}
            )
            response.raise_for_status()
            
            return ChatResponse(
                response=f"✓ Task marked as complete!",
                intent=intent,
                success=True
            )
        
        elif intent == "delete_task":
            task_identifier = params[0].strip() if params else None
            if not task_identifier:
                return ChatResponse(
                    response="Please specify which task to delete.",
                    intent=intent,
                    success=False
                )
            
            # Check if it's a task ID (number) or name
            if task_identifier.isdigit():
                task_id = task_identifier
            else:
                # Find task by name
                tasks = get_all_tasks(ACCESS_TOKEN)
                task = find_task_by_name(tasks, task_identifier)
                if not task:
                    return ChatResponse(
                        response=f"Task '{task_identifier}' not found.",
                        intent=intent,
                        success=False
                    )
                task_id = task["id"]
            
            response = requests.delete(
                f"{API_BASE_URL}/items/{task_id}",
                params={"access_token": ACCESS_TOKEN}
            )
            response.raise_for_status()
            
            return ChatResponse(
                response=f"Task deleted successfully!",
                intent=intent,
                success=True
            )

        else:
            return ChatResponse(response="I'm not sure what you want to do.", intent=intent, success=False)
    
    except requests.exceptions.HTTPError as e:
        return ChatResponse(response=f"API Error: {e.response.status_code} - {e.response.text}", intent=intent, success=False)
    except Exception as e:
        return ChatResponse(response=f"Error: {str(e)}", intent=intent, success=False)

@fastapi_app.get("/")
async def root():
    return {"message": "To-Do Chat API is running"}

@fastapi_app.get("/health")
async def health():
    return {"status": "healthy"}

# --- Streamlit Frontend (from frontend/streamlit_app.py) ---

def run_fastapi():
    # Use a different port for the FastAPI app when running locally within Streamlit
    # Streamlit runs on 8501 by default, so we'll use 8000 for FastAPI
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)

# Run FastAPI in a separate thread
# This ensures FastAPI starts when Streamlit starts
thread = threading.Thread(target=run_fastapi)
thread.daemon = True # Daemonize thread to exit when main program exits
thread.start()

# Page configuration
st.set_page_config(
    page_title="To-Do Chat Assistant",
    page_icon="✓",
    layout="centered"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Header
st.title("✓ To-Do Chat Assistant")
st.markdown("Manage your tasks using natural language!")

# Sidebar
with st.sidebar:
    st.header("Example")
    st.markdown("""
    - Add a task to buy milk
    - Show all tasks
    - List incomplete tasks
    - Mark buy milk as done
    - Delete task 2
    """)
    
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message..."):
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        try:
            # Streamlit frontend makes a request to the FastAPI backend running in the same process
            response = requests.post(
                "http://127.0.0.1:8000/chat", # FastAPI is running on port 8000
                json={
                    "message": prompt
                }
            )
            response.raise_for_status()
            assistant_response = response.json()["response"]
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": assistant_response
            })
            st.markdown(assistant_response)
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            st.error(error_msg)
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg
            })
