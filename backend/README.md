# Backend API for To-Do Chatbot

This FastAPI application serves as the backend for a to-do chatbot, integrating with an external "One List API" (`https://one-list-api.herokuapp.com`). It processes natural language commands from users, identifies their intent, and interacts with the external API to manage to-do tasks.

## Implementation Details

### Technologies Used
*   **FastAPI:** A modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints.
*   **Pydantic:** Used for data validation and settings management with Python type hints.
*   **Requests:** A simple, yet elegant, HTTP library for Python, used to interact with the external One List API.
*   **`re` module:** Python's built-in regular expression module for intent identification.
*   **`python-dotenv`:** For loading environment variables from a `.env` file.

### Core Logic

1.  **FastAPI Application Setup (`main.py`)**:
    *   The application is initialized using `FastAPI()`.
    *   **CORS Middleware**: `CORSMiddleware` is added to allow cross-origin requests, enabling the frontend (e.g., a Streamlit app) to communicate with this backend. `allow_origins=["*"]` is set for broad access during development.
    *   **Environment Variables**: `ACCESS_TOKEN` for the external API is loaded from environment variables using `dotenv`.

2.  **Data Models (`pydantic.BaseModel`)**:
    *   `ChatRequest`: Defines the structure of incoming chat messages, expecting a `message` string and an optional `access_token`.
    *   `ChatResponse`: Defines the structure of the responses sent back to the frontend, including a `response` message, the identified `intent`, and a `success` boolean.

3.  **Intent Identification (`identify_intent` function)**:
    *   A crucial part of the chatbot's natural language understanding.
    *   `INTENT_PATTERNS`: A dictionary where keys are recognized intents (e.g., "add_task", "list_tasks", "complete_task", "delete_task") and values are lists of regular expressions.
    *   The `identify_intent` function takes a user's `message`, converts it to lowercase, and attempts to match it against the regex patterns for each intent.
    *   If a match is found, it returns the `intent` and any captured `parameters` (e.g., the task name or ID extracted from the message). If no intent is matched, it defaults to "unknown".

4.  **External API Interaction Functions**:
    *   `get_all_tasks(token)`: Makes a GET request to the `/items` endpoint of the One List API to retrieve all tasks associated with the provided `access_token`.
    *   `find_task_by_name(tasks, name)`: A utility function to search through a list of tasks and find a task by its name, supporting case-insensitive partial matching.

5.  **Chat Endpoint (`/chat`)**:
    *   This is the primary endpoint (`POST /chat`) that receives user requests.
    *   It extracts the `access_token` (either from the request or environment variables).
    *   It calls `identify_intent` to understand the user's command.
    *   Based on the identified `intent`, it performs the following actions:
        *   **`add_task`**: Sends a POST request to `/items` to create a new task.
        *   **`list_tasks`**: Fetches all tasks and formats them into a readable list, indicating completion status.
        *   **`list_incomplete`**: Filters all tasks to show only incomplete ones.
        *   **`list_complete`**: Filters all tasks to show only complete ones.
        *   **`view_task`**: Fetches a specific task by its ID from `/items/{task_id}`.
        *   **`complete_task`**: Updates a task's status to complete. It can identify the task by either its ID or by searching for its name.
        *   **`delete_task`**: Deletes a task. It can identify the task by either its ID or by searching for its name.
    *   Each action constructs a `ChatResponse` with a user-friendly message, the intent, and a success/failure status.
    *   **Error Handling**: Includes `try-except` blocks to catch `requests.exceptions.HTTPError` (for API-specific errors) and general `Exception`s, returning appropriate error messages to the user.

6.  **Root and Health Endpoints**:
    *   `GET /`: A simple endpoint to confirm the API is running.
    *   `GET /health`: Provides a health check status.

## How to Run

1.  **Navigate to the `backend` directory.**
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    (Assuming `requirements.txt` in the root includes `fastapi`, `uvicorn`, `requests`, `pydantic`, `python-dotenv`)
3.  **Create a `.env` file** in the `backend` directory with your `ACCESS_TOKEN` for the One List API:
    ```
    ACCESS_TOKEN="your_one_list_api_access_token"
    ```
4.  **Run the application:**
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000
    ```
    The API will be accessible at `http://localhost:8000`.
