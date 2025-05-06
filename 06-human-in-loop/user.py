from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from langgraph.checkpoint.mongodb import MongoDBSaver
from langchain_core.tools import tool
from langgraph.types import interrupt

MONGO_DB_URI = "mongodb://admin:admin@localhost:27017"
config = {"configurable": {"thread_id": '4'}}
load_dotenv()

@tool()
def human_in_the_loop(query: str):
    """ Request assistance from human in the loop """
    human_response = interrupt({query: query})
    return human_response["data"]

tools = [human_in_the_loop]

llm = init_chat_model(model_provider="openai", model="gpt-4.1")
llm_with_tool = llm.bind_tools(tools = tools)

class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]

def chatbot(state: State):
    message = llm_with_tool.invoke(state["messages"])
    assert len(message.tool_calls) <= 1
    return {"messages": [message]}

graphBuilder = StateGraph(State)
graphBuilder.add_node("chatbot", chatbot)
graphBuilder.add_edge(START, "chatbot")
graphBuilder.add_edge("chatbot", END)

def create_chat_graph(checkpointer):
    return graphBuilder.compile(checkpointer=checkpointer)

def init():
    with MongoDBSaver.from_conn_string(MONGO_DB_URI) as checkpointer:
        graph_with_mongo = create_chat_graph(checkpointer)
        while True:
            user_message = input("You: ")
            for event in graph_with_mongo.stream({"messages": [{"role": "user", "content": user_message}]}, config, stream_mode="values"):
                if "messages" in event:
                    event["messages"][-1].pretty_print()
init()
