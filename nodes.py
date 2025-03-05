from langgraph.graph import StateGraph, MessagesState

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI  # Replace langchain_anthropic import

from typing import TypedDict, Literal, List
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage

# Define the state
class WorkflowState(TypedDict):
    messages: List[BaseMessage]

# Define the config
class GraphConfig(TypedDict):
    model_name: Literal["anthropic", "openai"]

def call_model(state: WorkflowState, config: GraphConfig):
    # Add model calling logic here
    # For example:
    if config["model_name"] == "anthropic":
        model = ChatAnthropic()
    else:
        model = ChatOpenAI()
    
    # Process messages and return updated state
    return state

def tool_node(state: WorkflowState):
    # Add tool execution logic here
    return state

def build_workflow(config: GraphConfig):
    # Create the graph
    workflow = StateGraph(WorkflowState)
    
    # Add nodes
    workflow.add_node("agent", call_model)
    workflow.add_node("action", tool_node)
    
    # Set entry point
    workflow.set_entry_point("agent")
    
    # Add edges
    workflow.add_edge("action", "agent")
    
    # Compile the graph
    return workflow.compile()

# To run the workflow:
if __name__ == "__main__":
    config = {"model_name": "anthropic"}  # or "openai"
    graph = build_workflow(config)
    
    # Initialize state
    initial_state = WorkflowState(messages=[])
    
    # Run the workflow
    final_state = graph.invoke(initial_state)