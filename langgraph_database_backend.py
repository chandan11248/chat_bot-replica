from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_groq import ChatGroq
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv

load_dotenv()

# LLM
llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0.7
)

# State
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# Node
def chat_node(state: ChatState):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# SQLite checkpoint
conn = sqlite3.connect("my_db.db", check_same_thread=False)
checkpointer = SqliteSaver(conn)

# Graph
graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)


def retrieve_all_threads():
    all_threads=set()
    items = checkpointer.list(None)  # get the list (or iterable)
    if items is not None:            # check it is not None
        for item in items:
            all_threads.add(item.config["configurable"]["thread_id"])
    else:
        all_threads.add(None)
        print("No items found.") 

    return list(all_threads)

