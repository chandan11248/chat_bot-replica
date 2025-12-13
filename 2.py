from langgraph_backend import chatbot
inital_state={"messages":"hi"}
CONFIG = {'configurable': {'thread_id': '1'}}
result=chatbot.invoke(inital_state,config=CONFIG)
print(result['messages'][-1].content)