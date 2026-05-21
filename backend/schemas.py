"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field, StrictStr, StrictInt
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime


class MaterialSharedItem(BaseModel):
    """Strict material shared during interaction."""
    type: StrictStr


class SampleDistributedItem(BaseModel):
    """Sample distributed during interaction."""
    name: StrictStr
    quantity: Optional[int] = None
    description: Optional[StrictStr] = None


class HCPInteractionBase(BaseModel):
    hcp_name: StrictStr
    hcp_type: Optional[StrictStr] = "Doctor"
    interaction_type: Optional[StrictStr] = "Meeting"
    date: StrictStr
    time: StrictStr
    attendees: Optional[StrictStr] = None
    topics_discussed: Optional[StrictStr] = None
    materials_shared: List[MaterialSharedItem] = Field(default_factory=list)
    samples_distributed: List[SampleDistributedItem] = Field(default_factory=list)
    sentiment: Optional[StrictStr] = "Neutral"
    outcomes: Optional[StrictStr] = None
    follow_up_actions: Optional[StrictStr] = None
    ai_suggestions: List[StrictStr] = Field(default_factory=list)
    ai_summary: Optional[StrictStr] = None
    extracted_entities: Dict[str, Any] = Field(default_factory=dict)


class HCPInteractionCreate(HCPInteractionBase):
    """Create interaction request"""
    pass


class HCPInteractionUpdate(BaseModel):
    """Update interaction request"""
    hcp_name: Optional[StrictStr] = None
    hcp_type: Optional[StrictStr] = None
    interaction_type: Optional[StrictStr] = None
    date: Optional[StrictStr] = None
    time: Optional[StrictStr] = None
    attendees: Optional[StrictStr] = None
    topics_discussed: Optional[StrictStr] = None
    materials_shared: Optional[List[MaterialSharedItem]] = None
    samples_distributed: Optional[List[SampleDistributedItem]] = None
    sentiment: Optional[StrictStr] = None
    outcomes: Optional[StrictStr] = None
    follow_up_actions: Optional[StrictStr] = None
    ai_suggestions: Optional[List[StrictStr]] = None
    ai_summary: Optional[StrictStr] = None
    extracted_entities: Optional[Dict[str, Any]] = None


class HCPInteractionResponse(BaseModel):
    """Response model for interaction"""
    id: int
    hcp_name: StrictStr
    hcp_type: StrictStr
    interaction_type: StrictStr
    date: StrictStr
    time: StrictStr
    attendees: Optional[StrictStr]
    topics_discussed: Optional[StrictStr]
    materials_shared: List[MaterialSharedItem]
    samples_distributed: List[SampleDistributedItem]
    sentiment: StrictStr
    outcomes: Optional[StrictStr]
    follow_up_actions: Optional[StrictStr]
    ai_suggestions: List[StrictStr]
    ai_summary: Optional[StrictStr]
    extracted_entities: Dict[str, Any]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = {
        "from_attributes": True,
    }


class AIMessageRequest(BaseModel):
    """AI chat message request"""
    message: StrictStr
    interaction_id: Optional[int] = None
    include_current_state: Optional[bool] = False
    current_interaction: Optional[Dict[str, Any]] = None


class AIMessageResponse(BaseModel):
    """AI chat message response"""
    status: StrictStr
    message: StrictStr
    tool_used: Optional[StrictStr] = None
    updated_interaction: Optional[HCPInteractionResponse] = None
    ai_response: StrictStr
    next_steps: Optional[List[StrictStr]] = None


class AIConversationHistoryResponse(BaseModel):
    """Response for conversation history"""
    id: int
    interaction_id: Optional[int]
    user_message: StrictStr
    ai_response: StrictStr
    tool_used: Optional[StrictStr]
    created_at: Optional[datetime]

    model_config = {
        "from_attributes": True,
    }


ToolName = Literal[
    "log_interaction",
    "edit_interaction",
    "get_interaction",
    "delete_interaction",
    "summarize_interaction",
]


class LogInteractionArguments(BaseModel):
    user_input: StrictStr


class EditInteractionArguments(BaseModel):
    current: Dict[str, Any]
    updates: Dict[str, Any]



class GetInteractionArguments(BaseModel):
    interaction_id: int


class DeleteInteractionArguments(BaseModel):
    interaction_id: int


class SummarizeInteractionArguments(BaseModel):
    interaction_data: Dict[str, Any]


class ToolCall(BaseModel):
    tool_name: ToolName
    arguments: Dict[str, Any]


class ToolExecutionRequest(BaseModel):
    """Request for direct tool execution"""
    tool_name: StrictStr
    interaction_data: Dict[str, Any]
    user_input: StrictStr


class ToolExecutionResponse(BaseModel):
    """Response from tool execution"""
    success: bool
    tool_used: StrictStr
    result: Dict[str, Any]
    updated_fields: Optional[Dict[str, Any]] = None
