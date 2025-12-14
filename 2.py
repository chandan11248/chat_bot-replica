import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph
# 1️⃣ SQLite connection
conn = sqlite3.connect("langgraph.db", check_same_thread=False)

# 2️⃣ Create checkpointer
checkpointer = SqliteSaver(conn)

# 3️⃣ Create graph
builder = StateGraph(dict)

def step(state):
    state["count"] = state.get("count", 0) + 1
    return state

builder.add_node("step", step)
builder.set_entry_point("step")

# 4️⃣ Compile with SQLite persistence
graph = builder.compile(checkpointer=checkpointer)

# 5️⃣ Run
print(graph.invoke({}))
print(graph.invoke({}))