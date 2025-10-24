from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import re
from typing import Optional, List, Dict
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer, util
app = FastAPI()

# CORS middleware for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
load_dotenv() 
# Configuration
API_BASE_URL = "https://one-list-api.herokuapp.com"
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "")
print(ACCESS_TOKEN)
class ChatRequest(BaseModel):
    message: str
    access_token: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    intent: str
    success: bool

model = SentenceTransformer("all-MiniLM-L6-v2")

# Intent examples
intents = {
    "add_task": [
        "add a new task",
        "create a task",
        "remind me to do something",
        "note this down",
    ],
    "list_tasks": [
        "show my tasks",
        "list all tasks",
        "what tasks do I have",
    ],
    "delete_task": [
        "delete a task",
        "remove this task",
        "erase my task",
    ]
}

# Precompute embeddings for intent examples
intent_embeddings = {
    intent: model.encode(samples, convert_to_tensor=True)
    for intent, samples in intents.items()
}

def detect_intent(user_input):
    user_emb = model.encode(user_input, convert_to_tensor=True)
    best_intent, best_score = None, 0

    for intent, examples_emb in intent_embeddings.items():
        score = util.cos_sim(user_emb, examples_emb).max().item()
        if score > best_score:
            best_intent, best_score = intent, score

    return best_intent, best_score

# Example
query = ""
intent, score = detect_intent(query)
print(intent, score)


def identify_intent(message: str) -> tuple:
    """Identify intent and extract parameters from user message"""
    message = message.lower().strip()
    
    for intent, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                params = match.groups() if match.groups() else None
                return intent, params
    
    return "unknown", None

def get_all_tasks(token: str) -> List[Dict]:
    """Fetch all tasks from API"""
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
    """Find task by name (case-insensitive partial match)"""
    name = name.lower().strip().strip('"\'')
    for task in tasks:
        if name in task.get("text", "").lower():
            return task
    return None

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process chat message and interact with One List API"""
    token = request.access_token or ACCESS_TOKEN
    
    if not token:
        return ChatResponse(
            response="Please configure your ACCESS_TOKEN to use this service.",
            intent="error",
            success=False
        )
    
    intent, params = identify_intent(request.message)
    
    try:
        # Handle different intents
        if intent == "add_task":
            task_name = params[0].strip() if params else None
            if not task_name:
                return ChatResponse(
                    response="Please specify a task name.",
                    intent=intent,
                    success=False
                )
            
            response = requests.post(
                f"{API_BASE_URL}/items",
                params={"access_token": token},
                json={"text": task_name}
            )
            response.raise_for_status()
            task = response.json()
            return ChatResponse(
                response=f"✓ Task created: \"{task['text']}\"",
                intent=intent,
                success=True
            )
        
        elif intent == "list_tasks":
            tasks = get_all_tasks(token)
            if not tasks:
                return ChatResponse(
                    response="You have no tasks.",
                    intent=intent,
                    success=True
                )
            
            task_list = "\n".join([
                f"{i+1}. {'✓' if t.get('complete') else '○'} {t['text']}"
                for i, t in enumerate(tasks)
            ])
            return ChatResponse(
                response=f"You have {len(tasks)} task(s):\n\n{task_list}",
                intent=intent,
                success=True
            )
        
        elif intent == "list_incomplete":
            tasks = get_all_tasks(token)
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
            tasks = get_all_tasks(token)
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
                params={"access_token": token}
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
                tasks = get_all_tasks(token)
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
                params={"access_token": token},
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
                tasks = get_all_tasks(token)
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
                params={"access_token": token}
            )
            response.raise_for_status()
            
            return ChatResponse(
                response=f"✓ Task deleted successfully!",
                intent=intent,
                success=True
            )
        
        else:
            return ChatResponse(
                response="I'm not sure what you want to do. You can:\n\n• Add a task: 'Add a task to buy milk'\n• List tasks: 'Show all tasks'\n• View a task: 'Show task 2'\n• Complete a task: 'Mark buy milk as done'\n• Delete a task: 'Delete buy milk'",
                intent=intent,
                success=False
            )
    
    except requests.exceptions.HTTPError as e:
        return ChatResponse(
            response=f"API Error: {e.response.status_code} - {e.response.text}",
            intent=intent,
            success=False
        )
    except Exception as e:
        return ChatResponse(
            response=f"Error: {str(e)}",
            intent=intent,
            success=False
        )

@app.get("/")
async def root():
    return {"message": "To-Do Chat API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
