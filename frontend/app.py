import streamlit as st
import requests
import os

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

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    
    st.divider()
    
    st.subheader("Example")
    st.markdown("""
    - Add a task to buy milk
    - Show all tasks
    - List incomplete tasks
    - Mark buy milk as done
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
    
    # Get response from backend
    with st.chat_message("assistant"):
        try:
            # Call the chat endpoint from main.py
            response = requests.post(
                "http://127.0.0.1:8000/chat",
                json={
                    "message": prompt
                }
            )
            response.raise_for_status()
            assistant_response = response.json()["response"]
            
            # Add and display assistant message
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