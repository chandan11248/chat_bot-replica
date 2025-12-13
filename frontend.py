import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage
CONFIG = {'configurable': {'thread_id': '1'}}

if 'message_history'not in st.session_state:
    st.session_state['message_history']=[]

for messages in st.session_state["message_history"]:
    with st.chat_message(messages['role']):
        st.text(messages['content'])

user_input = st.chat_input('Type here')
if user_input:

    # first add the message to message_history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)
    inital_state={"messages":user_input}
    result=chatbot.invoke(inital_state,config=CONFIG)
    ai_message = result['messages'][-1].content
# first add the message to message_history
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
    with st.chat_message('assistant'):
        st.text(ai_message)

    

