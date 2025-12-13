import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage
import time
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

 # Display with streaming effect
    with st.chat_message('assistant'):
        placeholder = st.empty()
        streamed_text = ""
        for char in ai_message:
            streamed_text += char
            placeholder.markdown(streamed_text + "▌")
            time.sleep(0.003)  # Adjust speed here
        placeholder.markdown(streamed_text)

# simple way 
        #  ai_message = st.write_stream(
        #     message_chunk.content for message_chunk, metadata in chatbot.stream(
        #         {'messages': [HumanMessage(content=user_input)]},
        #         config= {'configurable': {'thread_id': 'thread-1'}},
        #         stream_mode= 'messages'
        #     )
        # )

    # Add to history
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
    

