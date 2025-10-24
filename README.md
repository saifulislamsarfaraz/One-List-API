# To-Do Chat Assistant

A conversational interface for managing your to-do list using the One List API. This application allows you to interact with your to-do list using natural language.

## Version

1.0.0

## Technologies Used

*   **Python:** The core programming language for the project.
*   **FastAPI:** A modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints. Used for the backend.
*   **Streamlit:** An open-source app framework for Machine Learning and Data Science teams. Used for the interactive frontend UI.
*   **Requests:** An elegant and simple HTTP library for Python, used for making API calls to the One List API.
*   **python-dotenv:** A Python library for getting and setting environment variables from a `.env` file.
*   **Pydantic:** Data validation and settings management using Python type hints. Used in FastAPI for request and response models.
*   **Uvicorn:** A lightning-fast ASGI server, used to run the FastAPI application.

## Features

- **Add a task:** "Add"
- **List all tasks:** "Show"
- **List incomplete tasks:** "incomplete"
- **List complete tasks:** "Show my completed tasks"
- **Mark a task as complete:** "Mark as done"
- **Delete a task:** "Delete"

## Setup and Installation

1.  **Prerequisites:**
    *   Python 3.7+
    *   pip

2.  **Clone the repository (or download the files):**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

3.  **Create and activate a virtual environment:**
    *   **Windows:**
        ```bash
        python -m venv venv
        venv\Scripts\activate
        ```
    *   **macOS/Linux:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

4.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Create a `.env` file:**
    In the root of the project directory, create a file named `.env` and add your One List API access token:
    ```
    ACCESS_TOKEN="your_one_list_api_token"
    ```
    Replace `"your_one_list_api_token"` with your actual token.

## Usage

To run the application, you need to start both the backend and frontend servers in separate terminals.

1.  **Start the backend server:**
    ```bash
    uvicorn backend.main:app --reload
    ```
    The backend will be running at `http://127.0.0.1:8000`.

2.  **Start the frontend server:**
    ```bash
    streamlit run frontend/app.py
    ```
    The frontend will open in your web browser.

## Example Usage

Here's an example of a conversation with the To-Do Chat Assistant:

**User:** Add a new task to finish the project report.
**System:** ✓ Task created: "finish the project report"

**User:** What are my incomplete tasks?
**System:** You have 1 incomplete task(s):
1. ○ finish the project report

**User:** Mark "finish the project report" as done.
**System:** ✓ Task marked as complete!