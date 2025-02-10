from langgraph.graph import StateGraph, MessagesState

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI  # Replace langchain_anthropic import

from typing import TypedDict, Literal

from langgraph.graph import StateGraph, END

# Define the config
class GraphConfig(TypedDict):
    model_name: Literal["anthropic", "openai"]

# Define a new graph
workflow = StateGraph(WorkflowState, config_schema=GraphConfig)

# Define the two nodes we will cycle between
workflow.add_node("agent", call_model)
workflow.add_node("action", tool_node)

# Set the entrypoint as `agent`
# This means that this node is the first one called
workflow.set_entry_point("agent")

# We now add a normal edge from `tools` to `agent`.
# This means that after `tools` is called, `agent` node is called next.
workflow.add_edge("action", "agent")

# Finally, we compile it!
# This compiles it into a LangChain Runnable,
# meaning you can use it as you would any other runnable
graph = workflow.compile()


def build_workflow():
    graph = StateGraph(
        initial_state=WorkflowState(messages=[]),
        states=[],
        transitions=[],
    )

    return graph