from pydantic import BaseModel, Field
from typing import List, Optional

class InteractionState(BaseModel):
    hcp_name: Optional[str] = Field(None, description="Name of the Healthcare Professional")
    interaction_type: Optional[str] = Field("Meeting", description="Type of interaction, e.g., Meeting, Call, Email")
    date: Optional[str] = Field(None, description="Date in DD-MM-YYYY format")
    time: Optional[str] = Field(None, description="Time in HH:MM format")
    attendees: Optional[List[str]] = Field([], description="List of attendees")
    topics_discussed: Optional[str] = Field(None, description="Summary or raw notes of topics discussed")
    materials_shared: Optional[List[str]] = Field([], description="List of materials or brochures shared")
    samples_distributed: Optional[List[str]] = Field([], description="List of medical samples distributed")
    sentiment: Optional[str] = Field("Neutral", description="Sentiment: Positive, Neutral, or Negative")
    outcomes: Optional[str] = Field(None, description="Key outcomes or agreements")
    follow_up_actions: Optional[str] = Field(None, description="Next steps or tasks")

class ChatRequest(BaseModel):
    message: str
    current_state: InteractionState