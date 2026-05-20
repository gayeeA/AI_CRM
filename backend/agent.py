import os
import json
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
from backend.schema import InteractionState

load_dotenv()

# Define the local state schema for LangGraph routing loop
class AgentState(BaseModel):
    input_text: str
    current_form: InteractionState
    updated_form: InteractionState = Field(default_factory=InteractionState)
    chat_response: str = ""

# Ensure API Key is available
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is not set. Add it to backend/.env or your environment before starting the server."
    )

llm = ChatGroq(
    temperature=0.1,
    groq_api_key=GROQ_API_KEY,
    model_name="gemma2-9b-it"
)

# ----------------------------------------------------
# Define the 5 Explicit Tools for LangGraph Agent
# ----------------------------------------------------

# Tool 1: Log Interaction Data
class LogInteractionTool(BaseModel):
    """Capture raw structural components from conversational dialogue to populate form data completely."""
    hcp_name: str = Field(..., description="Extracted doctor name")
    sentiment: str = Field("Neutral", description="Must resolve exactly to: 'Positive', 'Neutral', or 'Negative'")
    topics_discussed: str = Field(..., description="Extracted context or subject summary")
    materials_shared: List[str] = Field(default=[], description="Extracted brochures, documentation items mentioned")

# Tool 2: Edit Interaction Data
class EditInteractionTool(BaseModel):
    """Modify specific existing structural values based on explicit corrections provided by user, leaving rest intact."""
    hcp_name: Optional[str] = Field(None, description="Updated doctor name if corrected")
    sentiment: Optional[str] = Field(None, description="Updated sentiment explicitly corrected: Positive, Neutral, Negative")
    topics_discussed: Optional[str] = Field(None, description="Updated summary description text modifications")

# Tool 3: SetFollowUpData
class SetFollowUpTool(BaseModel):
    """Extract action items, assignments, or schedule updates to populate future touchpoints fields."""
    follow_up_actions: str = Field(..., description="Action items, scheduling details, or tasks")

# Tool 4: AppendDistributedSamples
class AddSamplesTool(BaseModel):
    """Parse out product inventory samples distributed to the clinic."""
    samples_distributed: List[str] = Field(..., description="List of medical samples distributed")

# Tool 5: LogOutcomes
class LogOutcomesTool(BaseModel):
    """Synthesize explicit decisions, contract conclusions, or milestones reached during interaction."""
    outcomes: str = Field(..., description="Key resolutions or agreements reached")

# Bind tools straight to the Groq LLM structural engine
llm_with_tools = llm.bind_tools([
    LogInteractionTool, 
    EditInteractionTool, 
    SetFollowUpTool, 
    AddSamplesTool, 
    LogOutcomesTool
])

def process_intent_node(state: AgentState) -> Dict[str, Any]:
    system_prompt = (
        "You are an AI core module managing a life sciences HCP platform form state. "
        "Analyze the user's input request and determine which tool or combination of values need mapping. "
        f"Current form baseline configuration reads: {state.current_form.model_dump_json()}"
    )
    
    try:
        response = llm_with_tools.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=state.input_text)
        ])
    except Exception as exc:
        raise RuntimeError(
            "LLM invocation failed. Check GROQ_API_KEY and your Groq account settings. "
            f"Original error: {exc}"
        ) from exc
    
    # Initialize updated state with existing values
    working_data = state.current_form.model_dump()
    assistant_commentary = "I've handled that update for you."
    
    if response.tool_calls:
        for tool_call in response.tool_calls:
            args = tool_call['args']
            tool_name = tool_call['name']
            
            if tool_name == "LogInteractionTool":
                working_data.update({k: v for k, v in args.items() if v is not None})
                assistant_commentary = f"Logged interaction details for {args.get('hcp_name', 'HCP')} smoothly."
            
            elif tool_name == "EditInteractionTool":
                working_data.update({k: v for k, v in args.items() if v is not None})
                assistant_commentary = "Updated specific fields with your corrections."
                
            elif tool_name == "SetFollowUpTool":
                working_data["follow_up_actions"] = args.get("follow_up_actions")
                assistant_commentary = "Added follow-up operations into the dashboard state."
                
            elif tool_name == "AddSamplesTool":
                working_data["samples_distributed"] = list(set(working_data["samples_distributed"] + args.get("samples_distributed", [])))
                assistant_commentary = "Appended newly distributed medicine samples to registry."
                
            elif tool_name == "LogOutcomesTool":
                working_data["outcomes"] = args.get("outcomes")
                assistant_commentary = "Committed operational agreements and objectives achieved."
    else:
        # Fallback to structural chat interpretation if tool call was omitted
        assistant_commentary = response.content

    return {
        "updated_form": InteractionState(**working_data).model_dump(),
        "chat_response": assistant_commentary
    }

# Assemble LangGraph Workflow Engine
workflow = StateGraph(AgentState)
workflow.add_node("intent_processor", process_intent_node)
workflow.set_entry_point("intent_processor")
workflow.add_edge("intent_processor", END)

agent_executor = workflow.compile()