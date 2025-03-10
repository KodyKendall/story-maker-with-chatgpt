from langgraph.graph import StateGraph, MessagesState

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI  # Replace langchain_anthropic import

from typing import TypedDict, Literal, List, Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage
from dotenv import load_dotenv
import os

load_dotenv()

NUM_CHAPTERS = 5

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
            model_name="o1"  # Add a default model name for OpenAI
            # model_name="gpt-4o"  # Add a default model name for OpenAI
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
        f"You are writing a detailed outline for a book. Create an outline with {NUM_CHAPTERS} chapters, with brief descriptions of each chapter based on the user's message describing what they want you to write about:\n"
        f"---\n"
        f"{state.get('user_prompt', '')}\n"
        f"---\n"
    )
    
    model_response = call_model(prompt, state.get("model_name", "anthropic"))
    # model_response = call_model(prompt, state.get("model_name", "openai"))

    # For simplicity, let's assume the model returns an outline, with each line as a separate chapter.
    # You'd parse the response as needed in a real setting.
    # Example mock parse:
    # outline_lines = model_response.splitlines()
    # Save the outlines to state
    state["outline"] = model_response
    state["chapters"] = []
    state["current_chapter_index"] = 0
    state["final_story"] = ""
    return state

def chapter_implementation_node(state: WorkflowState) -> WorkflowState:
    """
    1. Using the outline, write a chapter based on the current chapter index.
    2. Append the result to state["chapters"].
    3. Update the final_story after each chapter.
    4. If more chapters remain, loop back to this node; otherwise, finalize the story.
    """
    outline = state.get("outline", [])
    idx = state.get("current_chapter_index", 0)
    
    # Safety check - ensure we have an outline
    if not outline:
        print("Warning: No outline found in state")
        state["final_story"] = "No outline was generated."
        return state
        
    print(f"Processing chapter {idx+1}/{NUM_CHAPTERS}")
    
    # Get the current story content (all previous chapters)
    current_story = state.get("final_story", "")
    
    # Write the next chapter based on its outline and previous content
    # chapter_title_or_description = outline[idx]
    prompt = (
        f"Write chapter {idx+1} based on this outline:\n"
        f"\"{outline}\"\n\n"
    )
    
    # Add previous chapters for context if they exist
    if current_story:
        prompt += (
            f"Here's the story so far:\n"
            f"---\n"
            f"{current_story}\n"
            f"---\n\n"
        )
    
    prompt += "Make this a complete, engaging chapter that advances the writing consistently with what came before."
    
    chapter_text = call_model(prompt, state.get("model_name", "anthropic"))
    
    # Store the newly written chapter
    chapters = state.get("chapters", [])
    new_chapter = f"Chapter {idx+1}: {chapter_text}"
    chapters.append(new_chapter)
    state["chapters"] = chapters
    
    # Update the final_story after each chapter
    if not current_story:
        state["final_story"] = new_chapter
    else:
        state["final_story"] = current_story + "\n\n" + new_chapter
    
    # Update the index for the next chapter
    state["current_chapter_index"] = idx + 1
    
    return state

def build_workflow():
    """
    Create a workflow with:
    - an outline node
    - a chapter writing node (looping until done)
    - finalize
    """
    workflow = StateGraph(WorkflowState)

    # Add nodes
    workflow.add_node("create_outline", chapter_outline_node)
    workflow.add_node("write_chapters", chapter_implementation_node)

    # Set entry point
    workflow.set_entry_point("create_outline")

    # Connect outline to first chapter
    workflow.add_edge("create_outline", "write_chapters")
    
    # Define a single router function instead of two separate conditions
    def chapter_router(state):
        idx = state.get("current_chapter_index", 0)
        if idx < NUM_CHAPTERS:
            print(f"More chapters needed (current: {idx}, total: {NUM_CHAPTERS})")
            return "write_chapters"
        else:
            print(f"All chapters complete (current: {idx}, total: {NUM_CHAPTERS})")
            return END
    
    # Add conditional edge with a single router function
    workflow.add_conditional_edges(
        "write_chapters",
        chapter_router
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