import streamlit as st
from nlp_logic import handle_chat

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

if prompt := st.chat_input("Type your message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = handle_chat(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.markdown(response)
