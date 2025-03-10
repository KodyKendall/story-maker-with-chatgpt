from langgraph.graph import StateGraph, MessagesState

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI  # Replace langchain_anthropic import

from typing import TypedDict, Literal, List, Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage
from dotenv import load_dotenv
import os

load_dotenv()

# Define the state
class WorkflowState(TypedDict):
    user_prompt: str                              # The user prompt describing the story to be written
    model_name: Optional[str]                     # Which model to call (optional)
    outline: Optional[List[str]]                  # A list of chapter outlines (optional)
    chapters: Optional[List[str]]                 # A list of fully written chapters (optional)
    current_chapter_index: Optional[int]          # Tracks which chapter we are currently writing (optional)
    final_story: Optional[str]                    # Combined text of all chapters (optional)
    messages: Optional[List["BaseMessage"]]       # Placeholder for conversation messages if needed (optional)

# Define the config
class GraphConfig(TypedDict):
    model_name: Literal["anthropic", "openai"]    # Which model to call

def call_model(prompt: str, model_name: str) -> str:
    """
    This is a mock model-calling function. In practice, you'd implement your
    actual call to Anthropic/OpenAI or any other LLM.
    """
    if model_name == "anthropic":
        claude_client = ChatAnthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            model_name="claude-3-5-sonnet-20240620"  # Add a default model name
        )
        try:
            response = claude_client.invoke(prompt)
            return response.content[0].text if isinstance(response.content, list) else response.content
        except Exception as e:
            print(f"Error in get_claude_response: {str(e)}")
            raise
    elif model_name == "openai":
        openai_client = ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name="gpt-4o"  # Add a default model name for OpenAI
        )
        try:
            response = openai_client.invoke(prompt)
            return response.content[0].text if isinstance(response.content, list) else response.content
        except Exception as e:
            print(f"Error in get_openai_response: {str(e)}")
            raise
    else:
        raise ValueError(f"Unsupported model_name: {model_name}")

def chapter_outline_node(state: WorkflowState) -> WorkflowState:
    """
    1. Generate a chapter outline from the user's prompt.
    2. Save that outline in the state.
    """
    # Call the LLM with a prompt to outline the story
    prompt = (
        f"Create a book outline with 10 chapters, with brief descriptions of each chapter based on the user prompt:\n"
        f"---\n"
        f"{state.get('user_prompt', '')}\n"
        f"---\n"
    )
    model_response = call_model(prompt, state.get("model_name", "anthropic"))

    # For simplicity, let's assume the model returns an outline, with each line as a separate chapter.
    # You'd parse the response as needed in a real setting.
    # Example mock parse:
    outline_lines = model_response.splitlines()
    # Save the outlines to state
    state["outline"] = [line.strip() for line in outline_lines if line.strip()]
    state["chapters"] = []
    state["current_chapter_index"] = 0
    state["final_story"] = ""
    return state

def chapter_implementation_node(state: WorkflowState) -> WorkflowState:
    """
    1. Using the outline, write a chapter based on the current chapter index.
    2. Append the result to state["chapters"].
    3. If more chapters remain, loop back to this node; otherwise, finalize the story.
    """
    outline = state.get("outline", [])
    idx = state.get("current_chapter_index", 0)

    # If we've written all chapters, go to "finalize" by skipping any new writing.
    if idx >= len(outline):
        # Combine all chapters to form the final story
        state["final_story"] = "\n\n".join(state.get("chapters", []))
        return state  # Moves on

    # Write the next chapter
    chapter_title_or_description = outline[idx]
    prompt = (
        f"Write a full, detailed chapter using the outline item:\n"
        f"\"{chapter_title_or_description}\"\n\n"
        f"Consider the chapters written so far:\n"
        f"{state.get('chapters', [])}\n"
        f"---\n"
    )
    chapter_text = call_model(prompt, state.get("model_name", "anthropic"))

    # Store the newly written chapter
    state["chapters"].append(chapter_text)
    state["current_chapter_index"] += 1

    # Decide next node: we can come back to chapter_implementation_node if more chapters are left
    return state

def build_workflow():
    """
    Create a workflow with:
    - an outline node
    - a chapter writing node (looping until done)
    - finalize
    """
    workflow = StateGraph(WorkflowState)

    # Add nodes - use different names to avoid conflict with state keys
    workflow.add_node("create_outline", chapter_outline_node)
    workflow.add_node("write_chapters", chapter_implementation_node)

    # Set entry point
    workflow.set_entry_point("create_outline")

    # Outline -> Chapters
    workflow.add_edge("create_outline", "write_chapters")
    
    # Define conditions as separate functions
    def more_chapters_condition(state):
        return state.get("current_chapter_index", 0) < len(state.get("outline", []))
        
    def all_chapters_done_condition(state):
        return state.get("current_chapter_index", 0) >= len(state.get("outline", []))
    
    # Chapters -> Chapters (loop back)
    workflow.add_conditional_edges(
        "write_chapters",
        {
            "write_chapters": more_chapters_condition,
            END: all_chapters_done_condition
        }
    )

    # Compile the graph
    return workflow.compile()

# To run the workflow:
if __name__ == "__main__":
    # Build the workflow (no config needed now)
    graph = build_workflow()

    # Initialize state with model_name directly in the state
    initial_state = WorkflowState(
        user_prompt="A sweeping fantasy epic about a wandering bard who uncovers an ancient secret that could change the kingdom forever.",
        outline=[],
        chapters=[],
        current_chapter_index=0,
        final_story="",
        messages=[],
        model_name="anthropic"  # Include model_name directly in state
    )

    # Run the workflow - no need to pass config anymore
    final_state = graph.invoke(initial_state)

    # Print final story
    print("\n--- FINAL STORY ---\n")
    print(final_state["final_story"])