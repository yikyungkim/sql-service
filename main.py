import streamlit as st
from typing_extensions import TypedDict

from langchain.chat_models import ChatOpenAI
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langgraph.graph import StateGraph, START, END  # Updated import
from langchain.agents.agent_types import AgentType
# from impala.dbapi import connect

# # 0. Impala Database Connection
# conn = connect(
#     host='xxx.com',
#     port=xxx,
# )
import sqlite3

import requests
from langchain_community.utilities.sql_database import SQLDatabase
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool


def get_engine_for_chinook_db():
    """Pull sql file, populate in-memory database, and create engine."""
    url = "https://raw.githubusercontent.com/lerocha/chinook-database/master/ChinookDatabase/DataSources/Chinook_Sqlite.sql"
    response = requests.get(url)
    sql_script = response.text

    connection = sqlite3.connect(":memory:", check_same_thread=False)
    connection.executescript(sql_script)
    return create_engine(
        "sqlite://",
        creator=lambda: connection,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )

engine = get_engine_for_chinook_db()
db = SQLDatabase(engine)


# 1. Define State Schema
class State(TypedDict):
    input: str
    generated_sql: str
    optimized_sql: str

# 2. Initialize Language Model
llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")

# 3. Create SQL Toolkit
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

# 4. Define Agent Nodes
def generate_sql(state: State):
    agent = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        agent_type=AgentType.OPENAI_FUNCTIONS,
        verbose=True
    )
    return {"generated_sql": agent.run(state["input"])}

def optimize_sql(state: State):
    agent = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        agent_type=AgentType.OPENAI_FUNCTIONS,
        verbose=True
    )
    return {"optimized_sql": agent.run(state["generated_sql"])}
    

# 5. Build LangGraph Workflow
builder = StateGraph(State)
builder.add_node("nl2sql", generate_sql)
builder.add_node("sql_optimizer", optimize_sql)
builder.set_entry_point("nl2sql")
builder.add_edge("nl2sql", "sql_optimizer")
builder.add_edge("sql_optimizer", END)
graph = builder.compile()


# 6. Streamlit UI
st.title("Enterprise SQL Assistant")
st.write("Natural Language to Optimized SQL Conversion")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Enter your data question"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Run through LangGraph workflow
    results = graph.invoke({"input": prompt,
                           "chat_history": st.session_state.messages})
    
    # Display results
    with st.chat_message("assistant"):
        response = f"""
        **Generated SQL:**
        ```
        {results['generated_sql']}
        ```
        
        **Optimized SQL:**
        ```
        {results['optimized_sql']}
        ```
        """
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
