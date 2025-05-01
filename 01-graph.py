from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from typing import Literal

class State(TypedDict):
    """
    A dictionary to hold the state of the application.
    """
    user_message: str
    ai_message: str
    is_coding_question: bool

def detect_query(state: State):   #node 1
    user_message = state["user_message"]
    state["is_coding_question"] = False
    return state

def route_edge(state: State) -> Literal["solve_coding_question" ,"solve_non_coding_question"]:
    """
    This function routes the edge based on the state of the application.
    """
    if state["is_coding_question"]:
        return "solve_coding_question"
    else:
        return "solve_non_coding_question"

def solve_coding_question(state: State):   #node 2
    user_message = state["user_message"]
    state["ai_message"] = "This is a coding question."
    return state

def solve_non_coding_question(state: State):   #node 3
    user_message = state["user_message"]
    state["ai_message"] = "This is not a coding question."
    return state

graphBuilder = StateGraph(State)
graphBuilder.add_node("detect_query", detect_query)
graphBuilder.add_node("solve_coding_question", solve_coding_question)
graphBuilder.add_node("solve_non_coding_question", solve_non_coding_question)
graphBuilder.add_node("route_edge", route_edge)

graphBuilder.add_edge(START, "detect_query")
graphBuilder.add_conditional_edges("detect_query", route_edge)

graphBuilder.add_edge("solve_coding_question", END)
graphBuilder.add_edge("solve_non_coding_question", END)

graph = graphBuilder.compile()

def call_graph():
    """
    This function calls the graph with the given state.
    """
    state = {
        "user_message": "What is the time complexity of quicksort?",
        "ai_message": "",
        "is_coding_question": False
    }
    result = graph.invoke(state)

    print(result)

if __name__ == "__main__":
    call_graph()
