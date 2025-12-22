from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_groq import ChatGroq
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from langgraph.prebuilt import ToolNode,tools_condition
from langchain_community.tools import DuckDuckGoSearchRun,tool
import requests
load_dotenv()
# import os
# # Set environment variable
# os.environ["LANGCHAIN_PROJECT"] = "backend llm"

# LLM
llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0.7
)

# Tools
search_tool = DuckDuckGoSearchRun(region="us-en")


@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA') 
    using Alpha Vantage with API key in the URL.
    """
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=DK8YGNCN6WOC4KQR"
    r = requests.get(url)
    return r.json()



tools = [search_tool, get_stock_price]
llm_with_tools = llm.bind_tools(tools)

# State
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# Node
def chat_node(state: ChatState):
    """LLM node that may answer or request a tool call."""
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

tool_node = ToolNode(tools)

# SQLite checkpoint
conn = sqlite3.connect("my_db.db", check_same_thread=False)
checkpointer = SqliteSaver(conn)

# 6. Graph
# -------------------
graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chat_node")

graph.add_conditional_edges("chat_node",tools_condition)
graph.add_edge('tools', 'chat_node')


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

