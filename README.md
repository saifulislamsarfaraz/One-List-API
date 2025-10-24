# To-Do Chat Assistant

A conversational interface for managing your to-do list using the One List API. This application allows you to interact with your to-do list using natural language.

## Version

1.0.0

## Project Structure

```
├── .gitignore
├── README.md
├── requirements.txt
├── backend/
│   └── main.py
├── frontend/
│   └── app.py
├── src/
│   ├── nlp_logic.py
│   └── streamlit_app.py
```

## Technologies Used

*   **Python:** The core programming language for the project.
*   **FastAPI:** A modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints. Used for the backend.
*   **Streamlit:** An open-source app framework for Machine Learning and Data Science teams. Used for the interactive frontend UI.
*   **Uvicorn:** A lightning-fast ASGI server, used to run the FastAPI application.
*   **Requests:** An elegant and simple HTTP library for Python, used for making API calls to the One List API.
*   **python-dotenv:** A Python library for getting and setting environment variables from a `.env` file.

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

There are two ways to run this application:

### Method 1: Separate Frontend and Backend

This method is suitable for local development and testing.

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

### Method 2: Streamlit Cloud Deployment

This method uses the `src` directory and is optimized for deployment on Streamlit Cloud.

```bash
streamlit run src/streamlit_app.py
```

The application will open in your web browser.

## Notes

*   The `backend` and `frontend` directories provide a traditional separation of concerns, which can be useful for development and testing. The `backend` is a FastAPI application, and the `frontend` is a Streamlit application that communicates with the backend.
*   The `src` directory contains a self-contained Streamlit application that includes the NLP logic. This is the recommended structure for deploying to Streamlit Cloud, as it simplifies the deployment process.

## Example Usage

Here's an example of a conversation with the To-Do Chat Assistant:

**User:** Add a new task to finish the project report.
**System:** ✓ Task created: "finish the project report"

**User:** What are my incomplete tasks?
**System:** You have 1 incomplete task(s):
1. ○ finish the project report

**User:** Mark "finish the project report" as done.
**System:** ✓ Task marked as complete!
