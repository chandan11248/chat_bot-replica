import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage, AIMessage
import uuid

# ***************************** utility functions *************************

def generate_thread_id():
    return str(uuid.uuid4())

def new_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    st.session_state['message_history'] = []
    # Add thread with empty title initially
    if thread_id not in [t['id'] for t in st.session_state["chat_threads"]]:
        st.session_state["chat_threads"].append({'id': thread_id, 'title': 'New Chat'})

def add_thread(thread_id, title='New Chat'):
    if thread_id not in [t['id'] for t in st.session_state["chat_threads"]]:
        st.session_state["chat_threads"].append({'id': thread_id, 'title': title})

def update_thread_title(thread_id, title):
    for thread in st.session_state["chat_threads"]:
        if thread['id'] == thread_id:
            # Truncate title if too long
            thread['title'] = title[:30] + "..." if len(title) > 30 else title
            break

def reset_chat():
    st.session_state['message_history'] = []

def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    return state.values.get('messages', [])

def show_message(thread_id):
    st.session_state['thread_id'] = thread_id
    messages = load_conversation(thread_id)
    st.session_state['message_history'] = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            st.session_state['message_history'].append({'role': 'user', 'content': msg.content})
        elif isinstance(msg, AIMessage):
            st.session_state['message_history'].append({'role': 'assistant', 'content': msg.content})

# **************************************** Session Setup ******************************
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []
    add_thread(st.session_state['thread_id'])

# **************************************** Sidebar UI *********************************

st.sidebar.title('LangGraph Chatbot')

st.sidebar.button('New Chat', on_click=new_chat)

st.sidebar.header('My Conversations')

# Display threads with title instead of ID
for thread in st.session_state['chat_threads'][::-1]:
    st.sidebar.button(
        thread['title'],
        key=thread['id'],
        on_click=show_message,
        args=(thread['id'],)
    )

# **************************************** Main UI ************************************

st.title("💬 Chat")
st.caption(f"Thread: {st.session_state['thread_id'][:8]}...")

# Loading the conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

user_input = st.chat_input('Type here')

if user_input:
    # First add the message to message_history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.markdown(user_input)

    # Update thread title with first user message
    if len(st.session_state['message_history']) == 1:
        update_thread_title(st.session_state['thread_id'], user_input)

    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

    # Stream AI response
    with st.chat_message("assistant"):
        def ai_only_stream():
            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages"
            ):
                if isinstance(message_chunk, AIMessage):
                    yield message_chunk.content

        ai_message = st.write_stream(ai_only_stream())

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})