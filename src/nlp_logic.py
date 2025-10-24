import requests
import re
from typing import Optional, List, Dict, Tuple
import os
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = "https://one-list-api.herokuapp.com"
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "")

# ---------------- Intent Patterns ----------------
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

# ---------------- Core Logic ----------------
def identify_intent(message: str) -> Tuple[str, Optional[Tuple]]:
    """Identify intent and extract parameters from user message"""
    message = message.lower().strip()
    for intent, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return intent, match.groups()
    return "unknown", None


def get_all_tasks(token: str) -> List[Dict]:
    """Fetch all tasks from API"""
    response = requests.get(f"{API_BASE_URL}/items", params={"access_token": token})
    response.raise_for_status()
    return response.json()


def find_task_by_name(tasks: List[Dict], name: str) -> Optional[Dict]:
    """Find task by name (case-insensitive partial match)"""
    name = name.lower().strip().strip('"\'')
    for task in tasks:
        if name in task.get("text", "").lower():
            return task
    return None


def handle_chat(message: str, token: Optional[str] = None) -> str:
    """Process user message and return response text"""
    token = token or ACCESS_TOKEN
    if not token:
        return "Please configure your ACCESS_TOKEN first."

    intent, params = identify_intent(message)

    try:
        if intent == "add_task":
            task_name = params[0].strip() if params else None
            if not task_name:
                return "Please specify a task name."
            
            response = requests.post(
                f"{API_BASE_URL}/items",
                params={"access_token": token},
                json={"text": task_name}
            )
            response.raise_for_status()
            task = response.json()
            return f"Task created: \"{task['text']}\""
        
        elif intent == "list_tasks":
            tasks = get_all_tasks(token)
            if not tasks:
                return "You have no tasks."
            
            task_list = "\n".join([
                f"{i+1}. {'Completed' if t.get('complete') else 'Incomplete'} - {t['text']}"
                for i, t in enumerate(tasks)
            ])
            return f"You have {len(tasks)} task(s):\n\n{task_list}"
        
        elif intent == "list_incomplete":
            tasks = get_all_tasks(token)
            incomplete = [t for t in tasks if not t.get("complete")]
            if not incomplete:
                return "You have no incomplete tasks."
            
            task_list = "\n".join([f"{i+1}. {t['text']}" for i, t in enumerate(incomplete)])
            return f"You have {len(incomplete)} incomplete task(s):\n\n{task_list}"
        
        elif intent == "list_complete":
            tasks = get_all_tasks(token)
            complete = [t for t in tasks if t.get("complete")]
            if not complete:
                return "You have no completed tasks yet."
            
            task_list = "\n".join([f"{i+1}. {t['text']}" for i, t in enumerate(complete)])
            return f"You have {len(complete)} completed task(s):\n\n{task_list}"
        
        elif intent == "view_task":
            task_id = params[0] if params else None
            if not task_id:
                return "Please specify a task number."
            
            response = requests.get(
                f"{API_BASE_URL}/items/{task_id}",
                params={"access_token": token}
            )
            response.raise_for_status()
            task = response.json()
            
            status = "Completed" if task.get("complete") else "Incomplete"
            return f"Task #{task_id}:\n\nName: {task['text']}\nStatus: {status}"
        
        elif intent == "complete_task":
            task_identifier = params[0].strip() if params else None
            if not task_identifier:
                return "Please specify which task to complete."
            
            if task_identifier.isdigit():
                task_id = task_identifier
            else:
                tasks = get_all_tasks(token)
                task = find_task_by_name(tasks, task_identifier)
                if not task:
                    return f"Task '{task_identifier}' not found."
                task_id = task["id"]
            
            response = requests.put(
                f"{API_BASE_URL}/items/{task_id}",
                params={"access_token": token},
                json={"complete": True}
            )
            response.raise_for_status()
            
            return "Task marked as complete."
        
        elif intent == "delete_task":
            task_identifier = params[0].strip() if params else None
            if not task_identifier:
                return "Please specify which task to delete."
            
            if task_identifier.isdigit():
                task_id = task_identifier
            else:
                tasks = get_all_tasks(token)
                task = find_task_by_name(tasks, task_identifier)
                if not task:
                    return f"Task '{task_identifier}' not found."
                task_id = task["id"]
            
            response = requests.delete(
                f"{API_BASE_URL}/items/{task_id}",
                params={"access_token": token}
            )
            response.raise_for_status()
            
            return "Task deleted successfully."
        
        else:
            return (
                "I'm not sure what you want to do. You can:\n"
                "- Add a task: 'Add a task to buy milk'\n"
                "- List tasks: 'Show all tasks'\n"
                "- View a task: 'Show task 2'\n"
                "- Complete a task: 'Mark buy milk as done'\n"
                "- Delete a task: 'Delete buy milk'"
            )

    except requests.exceptions.HTTPError as e:
        return f"API Error: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

