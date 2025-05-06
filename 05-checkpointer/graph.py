from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from langgraph.checkpoint.mongodb import MongoDBSaver

MONGO_DB_URI = "mongodb://admin:admin@localhost:27017"
config = {"configurable": {"thread_id": '1'}}
load_dotenv()
llm = init_chat_model(model_provider="openai", model="gpt-4.1")

class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]

def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

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
