from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv

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
graph = graphBuilder.compile()


def init():
    while True:
        user_message = input("You: ")
        for event in graph.stream({"messages": [{"role": "user", "content": user_message}]}, stream_mode="values"):
            if "messages" in event:
                event["messages"][-1].pretty_print()
init()
# This code is a simple chatbot that uses the OpenAI GPT-4.1 model to respond to user messages.
        